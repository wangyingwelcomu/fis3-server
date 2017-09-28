/**
 * @file fis-conf.js
 * @author 悟盈 <wangyingwelcomu@gmail.com>
 * FIS3 是面向前端的工程构建工具。解决前端工程中性能优化、资源加载（异步、同步、按需、预加载、依赖管理、合并、内嵌）、模块化开发、自动化工具、开发规范、代码部署等问题。
 * site:http://fis.baidu.com/fis3/docs/beginning/debug.html#发布到远端机器
 * ###功能-文件监听###
   为了方便开发，FIS3 支持文件监听，当启动文件监听时，修改文件会构建发布。而且其编译是增量的，编译花费时间少。
   FIS3 通过对 release 命令添加 -w 或者 --watch 参数启动文件监听功能。
   fis3 release -w
   添加 -w 参数时，程序不会执行终止；停止程序用快捷键 CTRL+c
 * ###功能-发布到远端机器###
    fis.match('*', {
      deploy: fis.plugin('http-push', {
        receiver: 'http://cq.01.p.p.baidu.com:8888/receiver.php',//接收脚本
        to: '/home/work/htdocs' // 注意这个是指的是测试机器的路径，而非本地机器
      })
    }
*/
/*
 * 构建dev模块下dev环境的的tpl和static文件(demo)
 * 执行命令：fis3 release devBuild -d ./fe --unique
 * 分析文件命令：fis3 inspect devBuild
*/
//设置项目源码文件指定目录
fis.media('devBuild').set('project.files', [
    '/fe/fe-mis/**'
]);
//指定过滤文件，覆盖不是叠加
fis.media('devBuild').set('project.ignore', [
    '/{*.md,**/*.md,**/*.txt}',
    '/fe/fe-mis/{**/*.html,**/*.php,**/*.json,**/*.sh}'
]);
//需要注意：files和ignore跨多级目录无法使用'**.tpl',必须使用'**/*.tpl'
fis.media('devBuild').match('/fe/fe-mis/statics/(**)', {
    useHash: true,
    release: 'output/mis/statics/$1',
    url: '/edmp/statics/$1'
});
fis.media('misFeBuild').match('/fe/fe-mis/statics/js/webuploader/**', {
    useHash: false,
});
fis.media('misFeBuild').match('/fe/fe-mis/views/(**.tpl)', {
    release: 'output/mis/views/$1'
});

/*
 * 发布mis模块dev环境
 * 执行命令：fis3 release devDeploy -w
 */
//设置项目源码文件指定目录
fis.media('devDeploy').set('project.files', [
    '/**',
]);
//过滤配置
fis.media('devDeploy').set('project.ignore', [
    '/{fis-conf.js,**/fis-conf.js}',//EXP:单文件过滤
    '/doc/**',//EXP:文件夹过滤
    '/{*.md,**/*.md}',//EXP:md后缀类型文件过滤
    '/{*.txt,**/*.txt}',
    '/{*.doc,**/*.doc}',
    '/{*.pdf,**/*.pdf}',
]);

//发布到远端机器
fis.media('devDeploy').match('*', {
  deploy: fis.plugin('http-push', {
    receiver: 'http://you.domain.com/fis3server/receiver.php',//接收端http链接
    to: '/home/www/htdocs/fis3server', // 注意这个是指的是测试机器的路径，而非本地机器
  })
})


//=====完美分割线====//
/*
 * fis3 release -h 获取更多帮助
 * Usage: fis3 release [media name]
 * Options:
   -h, --help                print this help message
   -d, --dest <path>         release output destination
   -l, --lint                with lint
   -w, --watch               monitor the changes of project 监控项目文件改变
   -L, --live                automatically reload your browser
   -c, --clean               clean compile cache 清楚编译缓存
   -u, --unique              use unique compile caching 唯一编译
   -r, --root <path>         specify project root 指定项目根目录
   -f, --file <filename>     specify the file path of `fis-conf.js`
   --no-color                disable colored output
   --verbose                 enable verbose mode
*/
/*
 * fis3 中的过滤符号说明
 * Options:
    * 匹配0或多个除了 / 以外的字符
    ? 匹配单个除了 / 以外的字符
    ** 匹配多个字符包括 /
    {} 可以让多个规则用 , 逗号分隔，起到或者的作用
    ! 出现在规则的开头，表示取反。即匹配不命中后面规则的文件
*/
//例子说明：
//需要注意的是，fis 中的文件路径都是以 / 开头的，所以编写规则时，请尽量严格的以 / 开头。
//当设置规则时，没有严格的以 / 开头，比如 a.js, 它匹配的是所有目录下面的 a.js, 包括：/a.js、/a/a.js、/a/b/a.js。 如果要严格只命中根目录下面的 /a.js, 请使用 fis.match('/a.js')。
//另外 /foo/*.js， 只会命中 /foo 目录下面的所有 js 文件，不包含子目录。 而 /foo/**/*.js 是命中所有子目录以及其子目录下面的所有 js 文件，不包含当前目录下面的 js 文件。 如果需要命中 foo 目录下面以及所有其子目录下面的 js 文件，请使用 /foo/**.js。
