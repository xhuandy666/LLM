import markdown


markdown_table = """
   | 序号 | 姓名 | 性别 | 身高(cm) | 
   | :--: | :--: | :--: | :--: | 
   | 1 | 小明 | 男 | 175 | 
   | 2 | 小华 | 女 | 170 | 
   | 3 | 小强 | 男 | 172 | 
   | 4 | 小芳 | 女 | 168 | 
   | 5 | 小刚 | 男 | 178 | 
   | 6 | 小丽 | 女 | 171 | 
   | 7 | 小杰 | 男 | 173 | 
   | 8 | 小婷 | 女 | 169 | 
   | 9 | 小勇 | 男 | 176 | 
   | 10 | 小雅 | 女 | 177 |
    """

    # 将markdown转换为HTML
html_table = markdown.markdown(markdown_table, extensions=['tables'])

    # 返回HTML形式的表格数据给前端页面
print(html_table)
