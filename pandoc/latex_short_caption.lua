if FORMAT ~= "latex" then return end

function Para (para)
  if #para.content ~= 1 then return end
  local img = para.content[1]
  if not img or img.t ~= 'Image' or #img.caption == 0
     or img.title:sub(1,4) ~= 'fig:'
     or not img.attributes['short-caption'] then
    return nil
  end

  local short_caption = pandoc.write(
    pandoc.read(img.attributes['short-caption']), FORMAT
  ):gsub('^%s*', ''):gsub('%s*$', '')  -- trim, removing surrounding whitespace

  local figure = pandoc.write(pandoc.Pandoc{para}, FORMAT)
  return pandoc.RawBlock(
    'latex',
    figure:gsub('\n\\caption', '\n\\caption[' .. short_caption .. ']')
  )
end