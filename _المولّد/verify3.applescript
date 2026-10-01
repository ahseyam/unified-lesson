on run argv
  set inPath to item 1 of argv
  set outPath to item 2 of argv
  set wantName to item 3 of argv
  tell application "Microsoft Word"
    activate
    delay 2
    open file name POSIX file inPath
    delay 6
    -- ⚠️ الحفظ بالاسم لا بالترتيب: محادثة موازية قد تفتح مستنداً فيتغيّر الترتيب بين الفحص والحفظ
    if not (exists document wantName) then return "NOT_FOUND"
    save as document wantName file format format PDF file name POSIX file outPath
    delay 4
    try
      close document wantName saving no
    end try
    return "OK"
  end tell
end run
