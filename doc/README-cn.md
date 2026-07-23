# ManimPreview

> [!NOTE]
> If you need an English doc, please move to `doc/README-en.md`

这是一个的通过网页预览manim动画的自动化工具。

这种工具并不是没人写，只是我尝试过的工具都不太好用，要么是与VSCode绑定太深（额。。。本人使用nvim），要么是缺少配置教程。

经过挣扎，我决定自己写一个，于是ManimPreview诞生了。

## 使用方法

### ManimPreview的下载

建议使用uv

### 命令的使用

提供manim-preview的命令行命令，在命令行输入`manim-preview [src_path] [scene_name]`即可开始使用。

其中`src_path`指的是需要监听文件的路径，scene_name是需要编译的场景名，目前只支持输入一个场景。

运行后，会开始监听目标文件（`src_path`）并自动打开默认浏览器，在当前文件夹下生成static/tmp.mp4文件储存临时文件，用于浏览器的读取。

每当文件保存时，会触发自动编译，更新tmp.mp4文件，重新加载到浏览器里。

这里推荐使用可以开启画中画的浏览器，如edge，这样就不用再频繁切换到浏览器的页面了。

比如：

![example](assets/use_with_edge.png)

> [!WARNING]
> 作者对自己的编程水平心知肚明，这个工具其实很脆弱，许多可能的类型和传参错误都没有写，
> 这也导致报错信息可能不太详细，所以仅限于能用，如果有任何问题，重开一遍就好了

## 可配置项

用户的配置文件写在manim-preview命令运行的文件夹内，文件名是`mpconfig.toml`

> [!NOTE]
> 所有的配置都要在运行manim-preview时写入，本工具未提供动态读取config的功能

列出所有可配置项：

```toml
[log]
# 用于控制server打印前端的等级
# 五个等级 critical > error > warning > info > debug > trace
# 等级越低，信息越多
web_level = "info"
# 控制台打印的等级
# 五个等级 CRITICAL > ERROR > WARNING > INFO > DEBUG > TRACE
# 注意这个是大写
console_level = "DEBUG"
# 控制台打印的格式
# 颜色的设置参见loguru的官方文档
console_formatter = "<level>{level}</level>: <level>{message}</level>"
# 文件输出的等级
# 等级和console_level一致
file_level = "INFO"
# log文件的路径和格式
# 参见loguru的官方文档
file_sink = "logs/{time:YYYY-MM-DD}.log"

[manim]
# 调用manim命令渲染时的质量参数
# 包括-qk > -qp > -qh > -qm > -ql，
# 越向右质量越高，渲染所需等的时间也越多
quality = "-ql"
# 从检测到文件变更到开始渲染的等待时间
# 用于去除短时间内的重复编译
render_interval = 0.5

[http]
# 开启浏览器页面和后端服务的端口，如有冲突，可更换
port = 8000
```

## 与nvim一同工作

我使用的是LazyNvim作为nvim的starter，所以nvim的配置文件里有nvim/lua/plugins。

这个文件夹内的所有文件都是自动被lazyvim加载的，可以直接写在这里。比如：

在nvim/lua/plugins/user_commands.lua里写入：

```lua
-- 自动运行`uv run preview %:p Scene_name`
local function start_preview(_)
  local scene_name = vim.fn.expand("<cword>")

  local curr_path = vim.fn.expand("%:p")

  -- 这里如果你使用的不是uv，那么改成正确的格式即可
  -- uv的好处就是不需要激活python的虚拟环境也能运行manim-preview命令
  local cmd = "uv run manim-preview " .. curr_path .. " " .. scene_name
  -- 这里使用了 toggleterm插件作为控制台
  -- 可以替换为nvim原生的terminal，只是新窗口的位置有点难受
  local Terminal = require("toggleterm.terminal").Terminal

  Terminal:new({
    cmd = cmd,
    direction = "vertical",
  }):toggle()
end
-- 注册一个nvim的user_command即可
vim.api.nvim_create_user_command(
  "PreviewManimAnimation", 
  start_preview, 
  { nargs = 0 }
)
-- lazyvim要求返回一个配置，这里需要返回空
return {}
```

> [!WARNING]
> 这段lua配置调用了Toggleterm的非原生插件，需要预先装上

保存重启nvim后，将光标停在你要预览的场景类名上，然后输入`:PreviewManimAnimation`，

nvim会开一个新窗口，自动运行`uv run manim-preview src_path scene_name`，之后你就可以愉快地创建manim的动画啦

> [!NOTE]
> plugins文件夹实际上不是用来写user_command的，我使用的方法是创建了nvim/lua/custom/commands.lua
> 然后在nvim/init.lua中加载：`require("custom.commands")`
