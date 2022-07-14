function fix_path (path)
    return '/pandoc/figs/' .. path
  end
  
  function Image (element)
    element.src = fix_path(element.src)
    return element
  end