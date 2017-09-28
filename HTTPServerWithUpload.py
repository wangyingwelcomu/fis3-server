#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple HTTP Server With Upload
Author: wangyingwelcomu@gmail.com
Brief: 基于BaseHTTPServer的webserver，主要包括文件查看、普通form表单文件上传功能、fis3组件(http://fis.baidu.com/)的文件上传功能
参考：https://github.com/python/cpython/blob/2.7/Lib/SimpleHTTPServer.py
Use : ./HTTPServerWithUpload.py port  port默认:8000
"""
import os,cgi,shutil,urllib,mimetypes
import posixpath
import BaseHTTPServer
import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Simple HTTP request handler with GET/HEAD/POST commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.

    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.
    """
    _version = '1.0'
    server_version = "SimpleHTTPWithUpload/" + _version

    def do_GET(self):
        """
        Serve a GET request
        """
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
    def do_HEAD(self):
        """
        Serve a HEAD request
        """
        f = self.send_head()
        if f:
            f.close()
    def do_POST(self):
        """
        Serve a POST request
        """
        form = cgi.FieldStorage(
             fp = self.rfile,
             headers = self.headers,
             environ = {
                        'REQUEST_METHOD':'POST',
                        'CONTENT_TYPE':self.headers.getheader('current-type')
                        }
             )
        #来源判断
        urlsource = ""; 
        if "to" in form:
            urlsource = "fis3";

        #基于来源数据处理逻辑
        if urlsource == 'fis3':
            bool,listData = self.do_post_fis3(form)
        else:
            bool,listData = self.do_post_form(form)
        
        #浏览器数据返回
        self.response(listData)

    def response(self,listData):
        """
        请求返回数据
        """
        f = StringIO()
        for data in listData:
            f.write(data)
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_post_fis3(self,form):
        """
        FIS3 POST文件上传
        """
        #保存fis3上传的文件
        for field in form.keys():
            fieldItem = form[field]
            filename = fieldItem.filename
            fieldValue  = fieldItem.value
            if field=='to':
                #文件绝对地址
                filePath = fieldValue
            elif  field=='file':
                try:
                    self.mkdir(filePath)
                    out = open(filePath, 'wb')
                    out.write(fieldValue)
                    out.close()
                    return (True,['{"errno":0,"errmsg":"成功"}'])
                except IOError:
                    return (False,['{"errno":1,"errmsg":"没有赋予写权限"}'])
        return (False,['{"errno":1,"errmsg":"请求参数缺失"}'])

    def do_post_form(self,form):
        """
        普通表单上传
        """
        r, info = self.deal_form_upload(form)
        print r, info, "by: ", self.client_address

        #返回的html
        L = [
            '<!DOCTYPE html><html><meta charset=\"utf-8\" />\n',
            "<title>Upload Result Page</title>\n",
            "<body>\n<h2>Upload Result Page</h2>\n",
            "<hr>\n"
            ];
        if r:
            L.extend(["<strong>Success:</strong>",info])
        else:
            L.extend(["<strong>Failed:</strong>",info])
        L.extend([
            "<br><a href=\"%s\">back</a>" % self.headers['referer'],
            "<hr><small>Powered By: chenai</body>\n</html>\n"
            ])
        return (True,L)

    def deal_form_upload(self,form):
        """
        普通表单文件上传
        """
        #判断是否是文件上传
        if not "file" in form:
            return (False, "只能上传文件并且form name='file'")
        #获取上传文件详情
        filePath = ''
        for field in form.keys():
            if field == 'file':
                #文件绝对地址
                fieldItem = form[field]
                filename = fieldItem.filename
                fileContent = fieldItem.value
        #检查文件名是否存在
        if not filename:
            return (False, "只能上传文件并且form name='file'")
        #文件名相同时,重新命名上传文件
        path = self.translate_path(self.path)
        filePath = os.path.join(path, filename)
        while os.path.exists(filePath):
            filePath += "_"
        try:
            out = open(filePath, 'wb')
            out.write(fileContent)
            out.close()
            return (True,"上传成功")
        except IOError:
            return (False,"没有赋予写权限")

    def mkdir(self,filePath):
        """
        递归创建多级文件夹
        """
        filePath = os.path.dirname(filePath)
        if not os.path.isdir(filePath):
            self.mkdir(filePath)
        else:
            return
        os.mkdir(filePath)

    def send_head(self):
        """
        Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """
        Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        L = [
            '<!DOCTYPE html><html><meta charset=\"utf-8\" />\n',
            "<title>>Directory listing</title>\n",
            "<body>\n<h2>Directory listing for %s</h2>\n" % displaypath,
            "<hr>\n",
            "<form ENCTYPE=\"multipart/form-data\" method=\"post\">",
            "<input name=\"file\" type=\"file\"/>",
            "<input type=\"submit\" value=\"upload\"/></form>\n",
            "<hr>\n<ul>\n"
            ];
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            L.append('<li><a href="%s">%s</a>\n' % (urllib.quote(linkname), cgi.escape(displayname)));

        L.append("</ul>\n<hr>\n</body>\n</html>\n");
        self.response(L)
        exit

    def translate_path(self, path):
        """
        Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """
        Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """
        Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types

    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


def main(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)

if __name__ == '__main__':
    main()
