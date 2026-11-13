# Hồ sơ chấm coherence, grounding và metadata

Các điểm gợi ý dưới đây do **Codex (AI)** đọc mẫu và chấm theo rubric. Tác giả cần tự đọc, sửa nếu cần và điền các cột human_* trong ba CSV. Không thay toàn bộ ô trống bằng điểm AI khi chưa kiểm tra.

- human_coherence_labels.csv: human_score 0/1/2, human_reason, human_reviewer.
- human_grounding_labels.csv: human_score 0/1/2, human_reason, human_reviewer.
- human_metadata_labels.csv: human_confirmed true/false về metadata đúng/đủ, human_reason, human_reviewer.

Các file nằm cùng thư mục với hồ sơ này. Giữ ID/rank/strategy khi sửa. Coherence: 0 không hiểu do cắt ý; 1 hiểu một phần; 2 tự hiểu và giữ trọn ý. Grounding: 0 không có evidence; 1 thiếu điều kiện/ngữ cảnh; 2 đủ bằng chứng để trả lời và truy nguồn.

## Coherence — 10 vị trí giống nhau cho mỗi cấu hình

### A-s01 — PDF page 23

Chunk `e26401a8dea3f466ea94f49a`, offsets 900–1400. Điểm AI: **1/2**. Starts with the end of a prior sentence and cuts symbolic computation mid-word; the program definition is partly understandable.

```text
chapter is called,
“The way of the program”.

On one level, you will be learning to program, a useful skill by itself. On another level, you
will use programming as a means to an end. As we go along, that end will become clearer.

1.1    What is a program?

Aprogramis a sequence of instructions that specifies how to perform a computation. The
computation might be something mathematical, such as solving a system of equations or
finding the roots of a polynomial, but it can also be a symbolic comp
```

### A-s02 — PDF page 24

Chunk `fb1788e22c2aa6855c2341b1`, offsets 1350–1850. Điểm AI: **1/2**. Starts mid-word in a recommendation, though Python version and interpreter statements are complete; surrounding context is missing.

```text
wise I recommend PythonAnywhere. I provide detailed
instructions for getting started athttp://tinyurl.com/thinkpython2e.

There are two versions of Python, called Python 2 and Python 3. They are very similar, so
if you learn one, it is easy to switch to the other. In fact, there are only a few differences you
will encounter as a beginner.  This book is written for Python 3, but I include some notes
about Python 2.

The  Pythoninterpreteris  a  program  that  reads  and  executes  Python  code.  
```

### A-s03 — PDF page 25

Chunk `12c25b06e8d78f2baa4aad09`, offsets 900–1400. Điểm AI: **1/2**. Starts inside the Hello World example and ends mid-sentence after arithmetic examples; useful but incomplete unit.

```text
llo,  World!'
This distinction will make more sense soon, but that’s enough to get started.

1.4    Arithmetic operators

After “Hello, World”, the next step is arithmetic.  Python providesoperators, which are
special symbols that represent computations like addition and multiplication.

The operators+,-, and*perform addition, subtraction, and multiplication, as in the fol-
lowing examples:
>>>  40  +  2
42
>>>  43  -  1
42
>>>  6  *  7
42
The operator/performs division:
>>>  84  /  2
42.0
You m
```

### A-s04 — PDF page 26

Chunk `8a122754b993f2aadcd91a62`, offsets 900–1400. Điểm AI: **1/2**. Starts inside a quoted numeric-string example; the comma-separated integer example is understandable but preceding context is cut.

```text
2.0'? They look like numbers, but they are in quotation
marks like strings.
>>>  type('2')
<class'str'>
>>>  type('42.0')
<class'str'>
They’re strings.

When you type a large integer, you might be tempted to use commas between groups of
digits, as in1,000,000. This is not a legalintegerin Python, but it is legal:
>>>  1,000,000
(1,  0,  0)
That’s not what we expected at all!  Python interprets1,000,000as a comma-separated
sequence of integers. We’ll learn more about this kind of sequence later.

```

### A-s05 — PDF page 27

Chunk `8e9eddff8acfc46ba6188d4e`, offsets 1350–1850. Điểm AI: **1/2**. Contains the complete ambiguity explanation but starts with a chopped parsing sentence and ends inside redundancy.

```text
his
process is calledparsing.

Although formal and natural languages have many features in common—tokens,  struc-
ture, and syntax—there are some differences:

ambiguity:Natural languages are full of ambiguity, which people deal with by using con-
       textual clues and other information.  Formal languages are designed to be nearly or
       completely unambiguous, which means that any statement has exactly one meaning,
       regardless of context.

redundancy:In order to make up for ambiguit
```

### A-s06 — PDF page 28

Chunk `5faac8f11aa60de5d0750393`, offsets 1350–1850. Điểm AI: **1/2**. Starts in the middle of the computer analogy and cuts the next debugging sentence; enough for partial meaning.

```text
 with them.  One approach is to think of
the computer as an employee with certain strengths, like speed and precision, and partic-
ular weaknesses, like lack of empathy and inability to grasp the big picture.

Your job is to be a good manager: find ways to take advantage of the strengths and mitigate
the weaknesses. And find ways to use your emotions to engage with the problem, without
letting your reactions interfere with your ability to work effectively.

Learning to debug can be frustrating, 
```

### A-s07 — PDF page 29

Chunk `6f939b3d03b347216e11055b`, offsets 900–1400. Điểm AI: **1/2**. Cuts off the formal-language label at the start and debugging definition at the end; intermediate glossary definitions are readable.

```text
e:Any one of the languages that people have designed for specific pur-
       poses, such as representing mathematical ideas or computer programs; all program-
       ming languages are formal languages.

token:One of the basic elements of the syntactic structure of a program, analogous to a
       word in a natural language.

syntax:The rules that govern the structure of a program.

parse:To examine a program and analyze the syntactic structure.

bug:An error in a program.

debugging:The proces
```

### A-s08 — PDF page 30

Chunk `41b1274fbff33551aca76d65`, offsets 0–500. Điểm AI: **1/2**. Includes complete questions but cuts the miles/kilometers question; exercise block lacks a complete final item.

```text
8                                                                                              Chapter 1. The way of the program

    4.  In math notation, leading zeros are ok, as in09.  What happens if you try this in Python?
        What about011?

    5.  What happens if you have two values with no operator between them?
Exercise 1.2.Start the Python interpreter and use it as a calculator.

    1.  How many seconds are there in 42 minutes 42 seconds?

    2.  How many miles are there in 10 k
```

### A-s09 — PDF page 31

Chunk `c187fb6680884d82ae0d6ad4`, offsets 450–950. Điểm AI: **1/2**. Begins inside the assignment explanation and ends inside variable naming; the state-diagram explanation remains partly understandable.

```text
 assigns a string to a new variable named
message; the second gives the integer17ton; the third assigns the (approximate) value of
πtopi.
A common way to represent variables on paper is to write the name with an arrow pointing
to its value.  This kind of figure is called astate diagrambecause it shows what state each
of the variables is in (think of it as the variable’s state of mind). Figure 2.1 shows the result
of the previous example.

2.2    Variable names

Programmers generally choose names
```

### A-s10 — PDF page 32

Chunk `eb6b364a2fd366372018e885`, offsets 900–1400. Điểm AI: **1/2**. Starts inside the keyword introduction and truncates the keyword table; the basic prohibition is understandable.

```text
t thatclassis one of Python’skeywords.   The interpreter uses keywords to
recognize the structure of the program, and they cannot be used as variable names.
Python 3 has these keywords:
False            class            finally        is                  return
None              continue      for                lambda          try
True              def                from              nonlocal      while
and                del                global          not                with
as            
```

### B-s01 — PDF page 23

Chunk `c36204a4bf139103b067a0cd`, offsets 946–1156. Điểm AI: **1/2**. Complete prose about learning programming, but the purpose referred to as an end remains vague and the next heading lacks its definition.

```text
On one level, you will be learning to program, a useful skill by itself. On another level, you
will use programming as a means to an end. As we go along, that end will become clearer.

1.1    What is a program?
```

### B-s02 — PDF page 24

Chunk `5472054f25fd2f82efbe6ac9`, offsets 1039–1470. Điểm AI: **1/2**. Browser recommendation paragraphs are intact, but that problem refers to context outside the chunk.

```text
To avoid that problem, I recommend that you start out running Python in a browser. Later,
when you are comfortable with Python, I’ll make suggestions for installing Python on your
computer.

There are a number of web pages you can use to run Python.  If you already have a fa-
vorite, go ahead and use it. Otherwise I recommend PythonAnywhere. I provide detailed
instructions for getting started athttp://tinyurl.com/thinkpython2e.
```

### B-s03 — PDF page 25

Chunk `ad721486e49cd445b5c2cf76`, offsets 564–1020. Điểm AI: **2/2**. Quotation marks, print-as-function and the Python 2 example form understandable complete statements; no cut word at either boundary.

```text
The quotation marks in the program mark the beginning and end of the text to be dis-
played; they don’t appear in the result.

The parentheses indicate thatprintis a function. We’ll get to functions in Chapter 3.

In Python 2, the print statement is slightly different; it is not a function, so it doesn’t use
parentheses.
>>>  print'Hello,  World!'
This distinction will make more sense soon, but that’s enough to get started.

1.4    Arithmetic operators
```

### B-s04 — PDF page 26

Chunk `14e86617a902442da738094b`, offsets 1053–1436. Điểm AI: **2/2**. The large-integer comma example includes the input, result and explanation; its main idea is complete.

```text
When you type a large integer, you might be tempted to use commas between groups of
digits, as in1,000,000. This is not a legalintegerin Python, but it is legal:
>>>  1,000,000
(1,  0,  0)
That’s not what we expected at all!  Python interprets1,000,000as a comma-separated
sequence of integers. We’ll learn more about this kind of sequence later.

1.6    Formal and natural languages
```

### B-s05 — PDF page 27

Chunk `8b450acd31f27b77b9302f2e`, offsets 1510–1805. Điểm AI: **2/2**. The ambiguity glossary-like paragraph is intact and explains both natural and formal languages.

```text
ambiguity:Natural languages are full of ambiguity, which people deal with by using con-
       textual clues and other information.  Formal languages are designed to be nearly or
       completely unambiguous, which means that any statement has exactly one meaning,
       regardless of context.
```

### B-s06 — PDF page 28

Chunk `ed66c4b67a23b156f34c4641`, offsets 1363–1810. Điểm AI: **2/2**. The computer-as-employee analogy and advice are intact and understandable together.

```text
One approach is to think of
the computer as an employee with certain strengths, like speed and precision, and partic-
ular weaknesses, like lack of empathy and inability to grasp the big picture.

Your job is to be a good manager: find ways to take advantage of the strengths and mitigate
the weaknesses. And find ways to use your emotions to engage with the problem, without
letting your reactions interfere with your ability to work effectively.
```

### B-s07 — PDF page 29

Chunk `dffc2711033367308fba6150`, offsets 886–1378. Điểm AI: **2/2**. All included glossary entries have their labels and full definitions; each is self-contained.

```text
formal language:Any one of the languages that people have designed for specific pur-
       poses, such as representing mathematical ideas or computer programs; all program-
       ming languages are formal languages.

token:One of the basic elements of the syntactic structure of a program, analogous to a
       word in a natural language.

syntax:The rules that govern the structure of a program.

parse:To examine a program and analyze the syntactic structure.

bug:An error in a program.
```

### B-s08 — PDF page 30

Chunk `c0563ca1ccac1f834e4bd05d`, offsets 0–458. Điểm AI: **2/2**. Each included Python experiment/question is complete, including the first calculator exercise; no final question is cut.

```text
8                                                                                              Chapter 1. The way of the program

    4.  In math notation, leading zeros are ok, as in09.  What happens if you try this in Python?
        What about011?

    5.  What happens if you have two values with no operator between them?
Exercise 1.2.Start the Python interpreter and use it as a calculator.

    1.  How many seconds are there in 42 minutes 42 seconds?
```

### B-s09 — PDF page 31

Chunk `ec6469b48f4f6d7b6e684129`, offsets 226–690. Điểm AI: **1/2**. Assignment examples and explanation are present, but the state-diagram topic begins without its following explanation.

```text
Anassignment statementcreates a new variable and gives it a value:
>>>  message  ='And  now  for  something  completely  different'
>>>  n  =  17
>>>  pi  =  3.1415926535897932
This example makes three assignments. The first assigns a string to a new variable named
message; the second gives the integer17ton; the third assigns the (approximate) value of
πtopi.
A common way to represent variables on paper is to write the name with an arrow pointing
to its value.
```

### B-s10 — PDF page 32

Chunk `4b016dd00049b7575d402120`, offsets 889–1388. Điểm AI: **1/2**. Keyword prohibition is complete, but the long keyword table is cut even by paragraph chunking.

```text
It turns out thatclassis one of Python’skeywords.   The interpreter uses keywords to
recognize the structure of the program, and they cannot be used as variable names.
Python 3 has these keywords:
False            class            finally        is                  return
None              continue      for                lambda          try
True              def                from              nonlocal      while
and                del                global          not                with
as
```

### C-s01 — PDF page 23

Chunk `c36204a4bf139103b067a0cd`, offsets 946–1156. Điểm AI: **1/2**. Complete prose about learning programming, but the purpose referred to as an end remains vague and the next heading lacks its definition. Identical B/C chunk verified.

```text
On one level, you will be learning to program, a useful skill by itself. On another level, you
will use programming as a means to an end. As we go along, that end will become clearer.

1.1    What is a program?
```

### C-s02 — PDF page 24

Chunk `5472054f25fd2f82efbe6ac9`, offsets 1039–1470. Điểm AI: **1/2**. Browser recommendation paragraphs are intact, but that problem refers to context outside the chunk. Identical B/C chunk verified.

```text
To avoid that problem, I recommend that you start out running Python in a browser. Later,
when you are comfortable with Python, I’ll make suggestions for installing Python on your
computer.

There are a number of web pages you can use to run Python.  If you already have a fa-
vorite, go ahead and use it. Otherwise I recommend PythonAnywhere. I provide detailed
instructions for getting started athttp://tinyurl.com/thinkpython2e.
```

### C-s03 — PDF page 25

Chunk `ad721486e49cd445b5c2cf76`, offsets 564–1020. Điểm AI: **2/2**. Quotation marks, print-as-function and the Python 2 example form understandable complete statements; no cut word at either boundary. Identical B/C chunk verified.

```text
The quotation marks in the program mark the beginning and end of the text to be dis-
played; they don’t appear in the result.

The parentheses indicate thatprintis a function. We’ll get to functions in Chapter 3.

In Python 2, the print statement is slightly different; it is not a function, so it doesn’t use
parentheses.
>>>  print'Hello,  World!'
This distinction will make more sense soon, but that’s enough to get started.

1.4    Arithmetic operators
```

### C-s04 — PDF page 26

Chunk `14e86617a902442da738094b`, offsets 1053–1436. Điểm AI: **2/2**. The large-integer comma example includes the input, result and explanation; its main idea is complete. Identical B/C chunk verified.

```text
When you type a large integer, you might be tempted to use commas between groups of
digits, as in1,000,000. This is not a legalintegerin Python, but it is legal:
>>>  1,000,000
(1,  0,  0)
That’s not what we expected at all!  Python interprets1,000,000as a comma-separated
sequence of integers. We’ll learn more about this kind of sequence later.

1.6    Formal and natural languages
```

### C-s05 — PDF page 27

Chunk `8b450acd31f27b77b9302f2e`, offsets 1510–1805. Điểm AI: **2/2**. The ambiguity glossary-like paragraph is intact and explains both natural and formal languages. Identical B/C chunk verified.

```text
ambiguity:Natural languages are full of ambiguity, which people deal with by using con-
       textual clues and other information.  Formal languages are designed to be nearly or
       completely unambiguous, which means that any statement has exactly one meaning,
       regardless of context.
```

### C-s06 — PDF page 28

Chunk `ed66c4b67a23b156f34c4641`, offsets 1363–1810. Điểm AI: **2/2**. The computer-as-employee analogy and advice are intact and understandable together. Identical B/C chunk verified.

```text
One approach is to think of
the computer as an employee with certain strengths, like speed and precision, and partic-
ular weaknesses, like lack of empathy and inability to grasp the big picture.

Your job is to be a good manager: find ways to take advantage of the strengths and mitigate
the weaknesses. And find ways to use your emotions to engage with the problem, without
letting your reactions interfere with your ability to work effectively.
```

### C-s07 — PDF page 29

Chunk `dffc2711033367308fba6150`, offsets 886–1378. Điểm AI: **2/2**. All included glossary entries have their labels and full definitions; each is self-contained. Identical B/C chunk verified.

```text
formal language:Any one of the languages that people have designed for specific pur-
       poses, such as representing mathematical ideas or computer programs; all program-
       ming languages are formal languages.

token:One of the basic elements of the syntactic structure of a program, analogous to a
       word in a natural language.

syntax:The rules that govern the structure of a program.

parse:To examine a program and analyze the syntactic structure.

bug:An error in a program.
```

### C-s08 — PDF page 30

Chunk `c0563ca1ccac1f834e4bd05d`, offsets 0–458. Điểm AI: **2/2**. Each included Python experiment/question is complete, including the first calculator exercise; no final question is cut. Identical B/C chunk verified.

```text
8                                                                                              Chapter 1. The way of the program

    4.  In math notation, leading zeros are ok, as in09.  What happens if you try this in Python?
        What about011?

    5.  What happens if you have two values with no operator between them?
Exercise 1.2.Start the Python interpreter and use it as a calculator.

    1.  How many seconds are there in 42 minutes 42 seconds?
```

### C-s09 — PDF page 31

Chunk `ec6469b48f4f6d7b6e684129`, offsets 226–690. Điểm AI: **1/2**. Assignment examples and explanation are present, but the state-diagram topic begins without its following explanation. Identical B/C chunk verified.

```text
Anassignment statementcreates a new variable and gives it a value:
>>>  message  ='And  now  for  something  completely  different'
>>>  n  =  17
>>>  pi  =  3.1415926535897932
This example makes three assignments. The first assigns a string to a new variable named
message; the second gives the integer17ton; the third assigns the (approximate) value of
πtopi.
A common way to represent variables on paper is to write the name with an arrow pointing
to its value.
```

### C-s10 — PDF page 32

Chunk `4b016dd00049b7575d402120`, offsets 889–1388. Điểm AI: **1/2**. Keyword prohibition is complete, but the long keyword table is cut even by paragraph chunking. Identical B/C chunk verified.

```text
It turns out thatclassis one of Python’skeywords.   The interpreter uses keywords to
recognize the structure of the program, and they cannot be used as variable names.
Python 3 has these keywords:
False            class            finally        is                  return
None              continue      for                lambda          try
True              def                from              nonlocal      while
and                del                global          not                with
as
```

## Grounding và metadata — 5 test mỗi cấu hình

Đọc cả top-3, đánh giá độ đủ bằng chứng; có thể grounding đủ dù metric exact-quote miss. Kiểm tra nguồn/trang/chương của từng rank với corpus_preview/PDF, ghi metadata đúng/đủ vào CSV.

### A-q16 — In chapter 5, what does floor division do, and in which direction does it round?

Đáp án gold: It divides two numbers and rounds down toward negative infinity to an integer.

Grounding AI: **2/2**. Rank 1, PDF 69, states floor division rounds toward negative infinity; source/page are available. Full answer supported.

Requested filter: `{'chapter': 5}`; applied: `None`.

**Rank 1** — PDF page 69, chapter 5, printed page 47; ID `b2380ad583395e0edcbb27a3`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
5.13. Glossary                                                                                                                                  47
5.13    Glossary

floor division:An operator, denoted//, that divides two numbers and rounds down (to-
       ward negative infinity) to an integer.

modulus operator:An operator, denoted with a percent sign (%), that works on integers
       and returns the remainder when one number is divided by another.

boolean expression:An expression whose value
```

**Rank 2** — PDF page 61, chapter 5, printed page 39; ID `8ff85d1cbfdea7d54a16c3b2`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
Chapter 5

Conditionals and recursion

The main topic of this chapter is theifstatement, which executes different code depending
on the state of the program. But first I want to introduce two new operators: floor division
and modulus.

5.1    Floor division and modulus

Thefloor divisionoperator,//, divides two numbers and rounds down to an integer. For
example, suppose the run time of a movie is 105 minutes.  You might want to know how
long that is in hours. Conventional division returns a floa
```

**Rank 3** — PDF page 62, chapter 5, printed page 40; ID `3531cd206b812006f1569cba`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
40                                                                                      Chapter 5. Conditionals and recursion

Also, you can extract the right-most digit or digits from a number.  For example,x  %  10
yields the right-most digit ofx(in base 10). Similarlyx  %  100yields the last two digits.

If you are using Python 2, division works differently.  The division operator,/, performs
floor division if both operands are integers, and floating-point division if either operand is
afloat
```

### A-q17 — If multiple conditions in an if/elif chain are true, which branch runs?

Đáp án gold: Only the first true branch runs; after that the chained statement ends.

Grounding AI: **2/2**. Rank 2, PDF 64, explicitly says only the first true branch runs and the statement ends. Full answer supported.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 69, chapter 5, printed page 47; ID `184c21198c3a4548d146e156`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
 determines  which
       branch runs.

compound statement:A statement that consists of a header and a body. The header ends
       with a colon (:). The body is indented relative to the header.

branch:One of the alternative sequences of statements in a conditional statement.

chained conditional:A conditional statement with a series of alternative branches.

nested conditional:A conditional statement that appears in one of the branches of another
       conditional statement.

return statement
```

**Rank 2** — PDF page 64, chapter 5, printed page 42; ID `002008679bdb0927db5dc927`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
 there
doesn’t have to be one.
if  choice  =='a':
      draw_a()
elif  choice  =='b':
      draw_b()
elif  choice  =='c':
      draw_c()
Each condition is checked in order. If the first is false, the next is checked, and so on. If one
of them is true, the corresponding branch runs and the statement ends. Even if more than
one condition is true, only the first true branch runs.

5.7    Nested conditionals

One conditional can also be nested within another.  We could have written the example in
th
```

**Rank 3** — PDF page 63, chapter 5, printed page 41; ID `bd846b6daf6f6963c9168971`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
e of the alternatives will run. The
alternatives are calledbranches, because they are branches in the flow of execution.

5.6    Chained conditionals

Sometimes there are more than two possibilities and we need more than two branches.
One way to express a computation like that is achained conditional:
```

### A-q18 — What two checks does the book recommend when accidental infinite recursion occurs?

Đáp án gold: Check for a base case that makes no recursive call, and check that execution is guaranteed to reach it.

Grounding AI: **2/2**. PDF 69 rank 2 defines a base case with no recursive call and infinite recursion as having no base case or never reaching it. Together with PDF 66 rank 1 this supports both checks, although the direct recommendation on PDF 67 is not retrieved in full.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 66, chapter 5, printed page 44; ID `0fa9dba37331ec2d714a12f9`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
5.10    Infinite recursion

If a recursion never reaches a base case, it goes on making recursive calls forever, and the
program never terminates.  This is known asinfinite recursion, and it is generally not a
good idea. Here is a minimal program with an infinite recursion:
```

**Rank 2** — PDF page 69, chapter 5, printed page 47; ID `2e707cd67455327bfe0eaecc`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
er
       conditional statement.

return statement:A statement that causes a function to end immediately and return to the
       caller.

recursion:The process of calling the function that is currently executing.

base case:A conditional branch in a recursive function that does not make a recursive call.

infinite recursion:A recursion that doesn’t have a base case, or never reaches it.  Eventu-
       ally, an infinite recursion causes a runtime error.

5.14    Exercises

Exercise 5.1.Thetimem
```

**Rank 3** — PDF page 67, chapter 5, printed page 45; ID `4534161f31fda20f6c05932a`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
5.11. Keyboard input                                                                                                                     45

def  recurse():
     recurse()
In most programming environments, a program with infinite recursion does not really run
forever. Python reports an error message when the maximum recursion depth is reached:
  File  "<stdin>",  line  2,  in  recurse
  File  "<stdin>",  line  2,  in  recurse
  File  "<stdin>",  line  2,  in  recurse
                          .

```

### A-q19 — After the user presses Enter, what type of value does input return?

Đáp án gold: A string containing what the user typed.

Grounding AI: **2/2**. PDF 67 rank 1 states input returns what was typed as a string after Enter; remaining hits show input/conversion context.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 67, chapter 5, printed page 45; ID `d5f1d80cdc3c1e32b06b23c0`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
ase that does not make a recursive call.  And if there is a base case, check
whether you are guaranteed to reach it.

5.11    Keyboard input

The programs we have written so far accept no input from the user. They just do the same
thing every time.
Python provides a built-in function calledinputthat stops the program and waits for the
user to type something.  When the user pressesReturnorEnter, the program resumes and
inputreturns what the user typed as a string.   In Python 2,  the same functio
```

**Rank 2** — PDF page 67, chapter 5, printed page 45; ID `089e49e2d5440b3657c847aa`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
yped as a string.   In Python 2,  the same function is called
raw_input.
>>>  text  =  input()
What  are  you  waiting  for?
>>>  text
'What  are  you  waiting  for?'
Before getting input from the user, it is a good idea to print a prompt telling the user what
to type.inputcan take a prompt as an argument:
>>>  name  =  input('What...is  your  name?\n')
What...is  your  name?
Arthur,  King  of  the  Britons!
>>>  name
'Arthur,  King  of  the  Britons!'
The sequence\nat the end of the prompt repr
```

**Rank 3** — PDF page 67, chapter 5, printed page 45; ID `2542e5afadf9c368dc0f5aa2`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
tons!'
The sequence\nat the end of the prompt represents anewline, which is a special character
that causes a line break. That’s why the user’s input appears below the prompt.
If you expect the user to type an integer, you can try to convert the return value toint:
>>>  prompt  ='What...is  the  airspeed  velocity  of  an  unladen  swallow?\n'
>>>  speed  =  input(prompt)
What...is  the  airspeed  velocity  of  an  unladen  swallow?
42
>>>  int(speed)
42
```

### A-q20 — Does the line identified by an error message necessarily contain the original mistake?

Đáp án gold: No. It shows where the problem was discovered; the actual mistake can be earlier in the code, sometimes on a previous line.

Grounding AI: **2/2**. PDF 68 rank 2 explicitly distinguishes where an error is discovered from an earlier actual cause; sufficient despite unrelated other hits.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 35, chapter 2, printed page 13; ID `0fcfa83aee8a99bd13d70ed7`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
o the right thing.  It will do something else.  Specifically, it
       will do what you told it to do.
       Identifying semantic errors can be tricky because it requires you to work backward
       by looking at the output of the program and trying to figure out what it is doing.
```

**Rank 2** — PDF page 68, chapter 5, printed page 46; ID `65c6a62e01958b652bfcde11`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
 x  =  5
>>>    y  =  6
   File  "<stdin>",  line  1
      y  =  6
      ^
IndentationError:  unexpected  indent
In this example, the problem is that the second line is indented by one space. But the error
message points toy, which is misleading.  In general, error messages indicate where the
problem was discovered, but the actual error might be earlier in the code, sometimes on a
previous line.
The same is true of runtime errors.  Suppose you are trying to compute a signal-to-noise
ratio in dec
```

**Rank 3** — PDF page 36, chapter 2, printed page 14; ID `6424ddce831fa31831fc9f08`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
 is meant for other programmers (or anyone read-
       ing the source code) and has no effect on the execution of the program.

syntax error:An error in a program that makes it impossible to parse (and therefore im-
       possible to interpret).

exception:An error that is detected while the program is running.

semantics:The meaning of a program.

semantic error:An error in a program that makes it do something other than what the
       programmer intended.

2.10    Exercises

Exercise 2.1.Re
```

### B-q16 — In chapter 5, what does floor division do, and in which direction does it round?

Đáp án gold: It divides two numbers and rounds down toward negative infinity to an integer.

Grounding AI: **2/2**. PDF 69 rank 1 explicitly gives downward direction toward negative infinity; PDF 61 rank 2 reinforces division semantics.

Requested filter: `{'chapter': 5}`; applied: `None`.

**Rank 1** — PDF page 69, chapter 5, printed page 47; ID `b682991e2f0b4f761994b81f`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
5.13. Glossary                                                                                                                                  47
5.13    Glossary

floor division:An operator, denoted//, that divides two numbers and rounds down (to-
       ward negative infinity) to an integer.

modulus operator:An operator, denoted with a percent sign (%), that works on integers
       and returns the remainder when one number is divided by another.
```

**Rank 2** — PDF page 61, chapter 5, printed page 39; ID `2b98dde0b6b256da468eacad`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
Thefloor divisionoperator,//, divides two numbers and rounds down to an integer. For
example, suppose the run time of a movie is 105 minutes.  You might want to know how
long that is in hours. Conventional division returns a floating-point number:
>>>  minutes  =  105
>>>  minutes  /  60
1.75
But we don’t normally write hours with decimal points.
```

**Rank 3** — PDF page 61, chapter 5, printed page 39; ID `a2f072734b1b10fc9d62cb41`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
Chapter 5

Conditionals and recursion

The main topic of this chapter is theifstatement, which executes different code depending
on the state of the program. But first I want to introduce two new operators: floor division
and modulus.

5.1    Floor division and modulus
```

### B-q17 — If multiple conditions in an if/elif chain are true, which branch runs?

Đáp án gold: Only the first true branch runs; after that the chained statement ends.

Grounding AI: **2/2**. PDF 64 rank 1 contains both first-true-branch and statement-ending rules. The missing introductory gold sentence does not prevent answering; strict documented-quote metric remains a miss.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 64, chapter 5, printed page 42; ID `d1d2237eb8f78970bbd79b6b`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
If the first is false, the next is checked, and so on. If one
of them is true, the corresponding branch runs and the statement ends. Even if more than
one condition is true, only the first true branch runs.

5.7    Nested conditionals
```

**Rank 2** — PDF page 63, chapter 5, printed page 41; ID `16091727f244bfc6304941c6`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
Since the condition must be true or false, exactly one of the alternatives will run. The
alternatives are calledbranches, because they are branches in the flow of execution.

5.6    Chained conditionals

Sometimes there are more than two possibilities and we need more than two branches.
One way to express a computation like that is achained conditional:
```

**Rank 3** — PDF page 64, chapter 5, printed page 42; ID `4c8eaaa575d95ce4bfab04f8`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
One conditional can also be nested within another.  We could have written the example in
the previous section like this:
if  x  ==  y:
      print('x  and  y  are  equal')
else:
      if  x  <  y:
            print('x  is  less  than  y')
      else:
            print('x  is  greater  than  y')
The outer conditional contains two branches. The first branch contains a simple statement.
The  second  branch  contains  anotherifstatement,  which  has  two  branches  of  its  own.
```

### B-q18 — What two checks does the book recommend when accidental infinite recursion occurs?

Đáp án gold: Check for a base case that makes no recursive call, and check that execution is guaranteed to reach it.

Grounding AI: **2/2**. PDF 69 rank 3 defines a non-recursing base case and the two causes of infinite recursion, supporting the two diagnostic checks by a short inference. PDF 66 adds context; rank 2 is only a header and is not useful.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 66, chapter 5, printed page 44; ID `0fa9dba37331ec2d714a12f9`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
5.10    Infinite recursion

If a recursion never reaches a base case, it goes on making recursive calls forever, and the
program never terminates.  This is known asinfinite recursion, and it is generally not a
good idea. Here is a minimal program with an infinite recursion:
```

**Rank 2** — PDF page 64, chapter 5, printed page 42; ID `e7c7c683faaf5d4ca925efa0`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
42                                                                                      Chapter 5. Conditionals and recursion
```

**Rank 3** — PDF page 69, chapter 5, printed page 47; ID `7f20827fe23b0a37d7059e96`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
return statement:A statement that causes a function to end immediately and return to the
       caller.

recursion:The process of calling the function that is currently executing.

base case:A conditional branch in a recursive function that does not make a recursive call.

infinite recursion:A recursion that doesn’t have a base case, or never reaches it.  Eventu-
       ally, an infinite recursion causes a runtime error.

5.14    Exercises
```

### B-q19 — After the user presses Enter, what type of value does input return?

Đáp án gold: A string containing what the user typed.

Grounding AI: **2/2**. PDF 67 rank 1 includes the complete statement that input returns a string; additional same-page examples support the context.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 67, chapter 5, printed page 45; ID `a1086c6d897fef1635c9db93`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
The programs we have written so far accept no input from the user. They just do the same
thing every time.
Python provides a built-in function calledinputthat stops the program and waits for the
user to type something.  When the user pressesReturnorEnter, the program resumes and
inputreturns what the user typed as a string.   In Python 2,  the same function is called
raw_input.
>>>  text  =  input()
What  are  you  waiting  for?
```

**Rank 2** — PDF page 67, chapter 5, printed page 45; ID `9fdf55826322be97578e5b57`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
That’s why the user’s input appears below the prompt.
If you expect the user to type an integer, you can try to convert the return value toint:
>>>  prompt  ='What...is  the  airspeed  velocity  of  an  unladen  swallow?\n'
>>>  speed  =  input(prompt)
What...is  the  airspeed  velocity  of  an  unladen  swallow?
42
>>>  int(speed)
42
```

**Rank 3** — PDF page 67, chapter 5, printed page 45; ID `d766b62febc4d2b37235e8dd`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
>>>  text
'What  are  you  waiting  for?'
Before getting input from the user, it is a good idea to print a prompt telling the user what
to type.inputcan take a prompt as an argument:
>>>  name  =  input('What...is  your  name?\n')
What...is  your  name?
Arthur,  King  of  the  Britons!
>>>  name
'Arthur,  King  of  the  Britons!'
The sequence\nat the end of the prompt represents anewline, which is a special character
that causes a line break.
```

### B-q20 — Does the line identified by an error message necessarily contain the original mistake?

Đáp án gold: No. It shows where the problem was discovered; the actual mistake can be earlier in the code, sometimes on a previous line.

Grounding AI: **2/2**. PDF 68 rank 1 explicitly says the actual error may occur earlier than the reported discovery line; full answer and traceability are present.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 68, chapter 5, printed page 46; ID `735ebe51723160c845e06b9f`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
In general, error messages indicate where the
problem was discovered, but the actual error might be earlier in the code, sometimes on a
previous line.
The same is true of runtime errors.  Suppose you are trying to compute a signal-to-noise
ratio in decibels.  The formula isSNR    db  =10 log    10(P  signal/P   noise).
```

**Rank 2** — PDF page 35, chapter 2, printed page 13; ID `5109861fb586dcfa1620c979`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
If  there  is  a  semantic  error  in  your  program,  it  will  run  without  generating  error
       messages, but it will not do the right thing.  It will do something else.  Specifically, it
       will do what you told it to do.
       Identifying semantic errors can be tricky because it requires you to work backward
       by looking at the output of the program and trying to figure out what it is doing.
```

**Rank 3** — PDF page 29, chapter 1, printed page 7; ID `a7bea1537f47b61957d07336`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
This kind of experiment helps you remember what you read; it also helps when you are programming,
because you get to know what the error messages mean.  It is better to make mistakes now and on
purpose than later and accidentally.

   1.  In a print statement, what happens if you leave out one of the parentheses, or both?

   2.  If you are trying to print a string, what happens if you leave out one of the quotation marks,
       or both?
```

### C-q16 — In chapter 5, what does floor division do, and in which direction does it round?

Đáp án gold: It divides two numbers and rounds down toward negative infinity to an integer.

Grounding AI: **2/2**. PDF 69 rank 1 explicitly gives downward direction toward negative infinity; PDF 61 rank 2 reinforces division semantics. Identical B/C top-3 verified; chapter filter is applied only to q16.

Requested filter: `{'chapter': 5}`; applied: `{'chapter': 5}`.

**Rank 1** — PDF page 69, chapter 5, printed page 47; ID `b682991e2f0b4f761994b81f`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
5.13. Glossary                                                                                                                                  47
5.13    Glossary

floor division:An operator, denoted//, that divides two numbers and rounds down (to-
       ward negative infinity) to an integer.

modulus operator:An operator, denoted with a percent sign (%), that works on integers
       and returns the remainder when one number is divided by another.
```

**Rank 2** — PDF page 61, chapter 5, printed page 39; ID `2b98dde0b6b256da468eacad`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
Thefloor divisionoperator,//, divides two numbers and rounds down to an integer. For
example, suppose the run time of a movie is 105 minutes.  You might want to know how
long that is in hours. Conventional division returns a floating-point number:
>>>  minutes  =  105
>>>  minutes  /  60
1.75
But we don’t normally write hours with decimal points.
```

**Rank 3** — PDF page 61, chapter 5, printed page 39; ID `a2f072734b1b10fc9d62cb41`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
Chapter 5

Conditionals and recursion

The main topic of this chapter is theifstatement, which executes different code depending
on the state of the program. But first I want to introduce two new operators: floor division
and modulus.

5.1    Floor division and modulus
```

### C-q17 — If multiple conditions in an if/elif chain are true, which branch runs?

Đáp án gold: Only the first true branch runs; after that the chained statement ends.

Grounding AI: **2/2**. PDF 64 rank 1 contains both first-true-branch and statement-ending rules. The missing introductory gold sentence does not prevent answering; strict documented-quote metric remains a miss. Identical B/C top-3 verified; chapter filter is applied only to q16.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 64, chapter 5, printed page 42; ID `d1d2237eb8f78970bbd79b6b`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
If the first is false, the next is checked, and so on. If one
of them is true, the corresponding branch runs and the statement ends. Even if more than
one condition is true, only the first true branch runs.

5.7    Nested conditionals
```

**Rank 2** — PDF page 63, chapter 5, printed page 41; ID `16091727f244bfc6304941c6`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
Since the condition must be true or false, exactly one of the alternatives will run. The
alternatives are calledbranches, because they are branches in the flow of execution.

5.6    Chained conditionals

Sometimes there are more than two possibilities and we need more than two branches.
One way to express a computation like that is achained conditional:
```

**Rank 3** — PDF page 64, chapter 5, printed page 42; ID `4c8eaaa575d95ce4bfab04f8`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
One conditional can also be nested within another.  We could have written the example in
the previous section like this:
if  x  ==  y:
      print('x  and  y  are  equal')
else:
      if  x  <  y:
            print('x  is  less  than  y')
      else:
            print('x  is  greater  than  y')
The outer conditional contains two branches. The first branch contains a simple statement.
The  second  branch  contains  anotherifstatement,  which  has  two  branches  of  its  own.
```

### C-q18 — What two checks does the book recommend when accidental infinite recursion occurs?

Đáp án gold: Check for a base case that makes no recursive call, and check that execution is guaranteed to reach it.

Grounding AI: **2/2**. PDF 69 rank 3 defines a non-recursing base case and the two causes of infinite recursion, supporting the two diagnostic checks by a short inference. PDF 66 adds context; rank 2 is only a header and is not useful. Identical B/C top-3 verified; chapter filter is applied only to q16.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 66, chapter 5, printed page 44; ID `0fa9dba37331ec2d714a12f9`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
5.10    Infinite recursion

If a recursion never reaches a base case, it goes on making recursive calls forever, and the
program never terminates.  This is known asinfinite recursion, and it is generally not a
good idea. Here is a minimal program with an infinite recursion:
```

**Rank 2** — PDF page 64, chapter 5, printed page 42; ID `e7c7c683faaf5d4ca925efa0`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
42                                                                                      Chapter 5. Conditionals and recursion
```

**Rank 3** — PDF page 69, chapter 5, printed page 47; ID `7f20827fe23b0a37d7059e96`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
return statement:A statement that causes a function to end immediately and return to the
       caller.

recursion:The process of calling the function that is currently executing.

base case:A conditional branch in a recursive function that does not make a recursive call.

infinite recursion:A recursion that doesn’t have a base case, or never reaches it.  Eventu-
       ally, an infinite recursion causes a runtime error.

5.14    Exercises
```

### C-q19 — After the user presses Enter, what type of value does input return?

Đáp án gold: A string containing what the user typed.

Grounding AI: **2/2**. PDF 67 rank 1 includes the complete statement that input returns a string; additional same-page examples support the context. Identical B/C top-3 verified; chapter filter is applied only to q16.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 67, chapter 5, printed page 45; ID `a1086c6d897fef1635c9db93`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
The programs we have written so far accept no input from the user. They just do the same
thing every time.
Python provides a built-in function calledinputthat stops the program and waits for the
user to type something.  When the user pressesReturnorEnter, the program resumes and
inputreturns what the user typed as a string.   In Python 2,  the same function is called
raw_input.
>>>  text  =  input()
What  are  you  waiting  for?
```

**Rank 2** — PDF page 67, chapter 5, printed page 45; ID `9fdf55826322be97578e5b57`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
That’s why the user’s input appears below the prompt.
If you expect the user to type an integer, you can try to convert the return value toint:
>>>  prompt  ='What...is  the  airspeed  velocity  of  an  unladen  swallow?\n'
>>>  speed  =  input(prompt)
What...is  the  airspeed  velocity  of  an  unladen  swallow?
42
>>>  int(speed)
42
```

**Rank 3** — PDF page 67, chapter 5, printed page 45; ID `d766b62febc4d2b37235e8dd`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
>>>  text
'What  are  you  waiting  for?'
Before getting input from the user, it is a good idea to print a prompt telling the user what
to type.inputcan take a prompt as an argument:
>>>  name  =  input('What...is  your  name?\n')
What...is  your  name?
Arthur,  King  of  the  Britons!
>>>  name
'Arthur,  King  of  the  Britons!'
The sequence\nat the end of the prompt represents anewline, which is a special character
that causes a line break.
```

### C-q20 — Does the line identified by an error message necessarily contain the original mistake?

Đáp án gold: No. It shows where the problem was discovered; the actual mistake can be earlier in the code, sometimes on a previous line.

Grounding AI: **2/2**. PDF 68 rank 1 explicitly says the actual error may occur earlier than the reported discovery line; full answer and traceability are present. Identical B/C top-3 verified; chapter filter is applied only to q16.

Requested filter: `None`; applied: `None`.

**Rank 1** — PDF page 68, chapter 5, printed page 46; ID `735ebe51723160c845e06b9f`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
In general, error messages indicate where the
problem was discovered, but the actual error might be earlier in the code, sometimes on a
previous line.
The same is true of runtime errors.  Suppose you are trying to compute a signal-to-noise
ratio in decibels.  The formula isSNR    db  =10 log    10(P  signal/P   noise).
```

**Rank 2** — PDF page 35, chapter 2, printed page 13; ID `5109861fb586dcfa1620c979`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
If  there  is  a  semantic  error  in  your  program,  it  will  run  without  generating  error
       messages, but it will not do the right thing.  It will do something else.  Specifically, it
       will do what you told it to do.
       Identifying semantic errors can be tricky because it requires you to work backward
       by looking at the output of the program and trying to figure out what it is doing.
```

**Rank 3** — PDF page 29, chapter 1, printed page 7; ID `a7bea1537f47b61957d07336`.
Nguồn: https://greenteapress.com/thinkpython2/thinkpython2.pdf

```text
This kind of experiment helps you remember what you read; it also helps when you are programming,
because you get to know what the error messages mean.  It is better to make mistakes now and on
purpose than later and accidentally.

   1.  In a print statement, what happens if you leave out one of the parentheses, or both?

   2.  If you are trying to print a string, what happens if you leave out one of the quotation marks,
       or both?
```
