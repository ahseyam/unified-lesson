on run argv
  set inPath to item 1 of argv
  set outPath to item 2 of argv
  set wantName to item 3 of argv
  tell application "Microsoft Word"
    activate
    set display alerts to none
    delay 1
    open file name POSIX file inPath
    delay 7
    if not (exists document wantName) then
      set display alerts to alerts all
      return "NOT_FOUND"
    end if
    save as document wantName file format format document file name POSIX file outPath
    delay 3
    try
      close document wantName saving no
    end try
    set display alerts to alerts all
    return "OK"
  end tell
end run
