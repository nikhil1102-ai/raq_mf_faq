import re

with open('ui/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Include ui/app.js
html = html.replace('</head>', '<script src=\"/static/app.js\" defer></script>\n</head>')

# 2. Add IDs to elements
html = html.replace('<div class=\"flex-1 overflow-y-auto px-container-padding-mobile md:px-container-padding-desktop py-stack-lg flex flex-col items-center justify-center min-h-[500px]\">', 
                    '<div id=\"chat-canvas\" class=\"flex-1 overflow-y-auto px-container-padding-mobile md:px-container-padding-desktop py-stack-lg flex flex-col items-center justify-center min-h-[500px]\">')

html = html.replace('<div class=\"w-full max-w-4xl flex flex-col items-center text-center\">', 
                    '<div id=\"welcome-view\" class=\"w-full max-w-4xl flex flex-col items-center text-center\">')

html = html.replace('<!-- Card 1 -->\n<button', '<!-- Card 1 -->\n<button id=\"card-1\"')
html = html.replace('<!-- Card 2 -->\n<button', '<!-- Card 2 -->\n<button id=\"card-2\"')
html = html.replace('<!-- Card 3 -->\n<button', '<!-- Card 3 -->\n<button id=\"card-3\"')

html = html.replace('<input class=\"w-full', '<input id=\"chat-input\" class=\"w-full')
html = html.replace('<!-- Send Button -->\n<button', '<!-- Send Button -->\n<button id=\"send-btn\"')

# 3. Replace the sidebar schemes list
old_schemes = '''<!-- Supported Schemes List (10 Items) -->
<div class=\"mt-4 flex flex-col gap-2 overflow-y-auto pr-2 pb-4\">
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Prudential Flexicap Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Prudential Bluechip Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Prudential Liquid Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Pru Value Discovery Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Pru Balanced Advantage</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Tax Saver ELSS Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Small Cap Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Liquid Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Large Cap Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Multi Cap Fund</div>
</div>'''

new_schemes = '''<!-- Supported Schemes List (6 Items) -->
<div class=\"mt-4 flex flex-col gap-2 overflow-y-auto pr-2 pb-4\">
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Prudential Large Cap Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Prudential Flexicap Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">ICICI Prudential Multicap Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Nifty 500 Momentum 50</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Large Cap Fund</div>
<div class=\"text-caption-sm font-caption-sm text-on-surface-variant px-3 py-1.5 hover:bg-surface-variant rounded-md cursor-pointer transition-colors\">Nippon India Tax Saver ELSS Fund</div>
</div>'''

html = html.replace(old_schemes, new_schemes)

# Hide CTA View All Schemes
html = html.replace('View All Schemes', 'View All Schemes (Hidden)')
html = html.replace('<button class=\"mt-auto bg-primary-container text-on-primary', '<button class=\"hidden mt-auto bg-primary-container text-on-primary')
html = html.replace('View 10 Supported Schemes', 'View Supported Schemes')

with open('ui/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
