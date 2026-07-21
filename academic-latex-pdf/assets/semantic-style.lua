-- Render only explicitly reviewed semantic quotation annotations in Kai.

local function wrap_in_kaiti(inlines)
  local result = pandoc.List:new({pandoc.RawInline('latex', '{\\quotezh ')})
  result:extend(inlines)
  result:insert(pandoc.RawInline('latex', '}'))
  return result
end

function Span(element)
  if element.classes:includes('semantic-inline-quote') then
    return wrap_in_kaiti(element.content)
  end
end

function Div(element)
  if element.classes:includes('semantic-quote') then
    local blocks = pandoc.List:new({pandoc.RawBlock('latex', '\\begingroup\\quotezh')})
    blocks:extend(element.content)
    blocks:insert(pandoc.RawBlock('latex', '\\par\\endgroup'))
    return blocks
  end
end
