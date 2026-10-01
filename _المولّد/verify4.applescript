on run argv
  set inPath to item 1 of argv
  set outPath to item 2 of argv
  set wantName to item 3 of argv
  tell application "Microsoft Word"
    activate
    -- ⚠️ نسخةٌ عالقة من محاولةٍ سابقة تمنع الفتح، فتُغلق أولاً بلا حفظ
    try
      if exists document wantName then close document wantName saving no
    end try
    delay 1
    open file name POSIX file inPath
    -- ⚠️ الانتظار بظهور المستند لا بمدةٍ ثابتة: التأخير الثابت يُخفق حين يبطؤ وورد
    set n to 0
    repeat until (exists document wantName) or n > 40
      delay 1
      set n to n + 1
    end repeat
    if not (exists document wantName) then return "NOT_FOUND"
    delay 2
    save as document wantName file format format PDF file name POSIX file outPath
    delay 3
    try
      close document wantName saving no
    end try
    return "OK"
  end tell
end run
