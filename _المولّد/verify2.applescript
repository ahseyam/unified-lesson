on run argv
  set inPath to item 1 of argv
  set outPath to item 2 of argv
  set wantName to item 3 of argv
  tell application "Microsoft Word"
    activate
    delay 2
    open file name POSIX file inPath
    delay 6
    set n to count documents
    set idx to 0
    repeat with i from 1 to n
      if (name of document i) is wantName then set idx to i
    end repeat
    if idx is 0 then return "NOT_FOUND (فُتح بدلاً منه: " & (name of document 1) & ")"
    save as document idx file format format PDF file name POSIX file outPath
    delay 4
    try
      close document idx saving no
    end try
    return "OK"
  end tell
end run
