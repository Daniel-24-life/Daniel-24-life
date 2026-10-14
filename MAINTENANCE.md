# 主页维护

个人介绍和结尾是手写区。精选项目、阅读导航与近期发布由 AIfile 的
catalog/projects.json 生成，只覆盖 portfolio 标记区。

catalog-source.json 固定登记表来源提交。CI 获取这个提交并复核生成区，避免
跟随远端 main 自动改变主页。需要更新时先完善、检查并发布 AIfile，再运行其
render_portfolio.py 指定本仓库路径和新的完整来源 SHA。

不使用统计卡、贡献动画或自动发布任务。头像、名称和用户名保持原样。
