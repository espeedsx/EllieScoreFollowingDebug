An Introduction to Serpent

## Roger B. Dannenberg

Serpent is a programming language inspired by Python. Like Python, it has a simple, minimal syntax, dynamic typing, and support for object-oriented programming. Serpent also draws inspiration from XLisp, Squeak, SmallTalk, Ruby, and Basic. Why another language? Serpent is designed for use in real-time systems, especially interactive multimedia systems. Serpent is unique in providing the following combination of features:

Real-time garbage collection: Squeak has a pretty fast generational scavenging collector, but Serpent does even better with a parallel mark-sweep garbage collector.

Multiple virtual machines: Multiple independent instances of Serpent can run concurrently in one address space. This allows each thread to have its own copy of Serpent and to rely on the OS for scheduling and preemption.

I recommend Python to anyone who does not need these features. Serpent has some other differences from Python that reflect both the designer's personal tastes and limited resources:

Symbols (unique strings) are a primitive data type. Serpent does not have name spaces.

Serpent is more of an expression language than Python: every statement returns a value. Serpent has non-preemptive threads and support for precisely timed execution.

Python has many more libraries.

# Topics

Types

Serpent has the following primitive types:

Integer -- a 64-bit signed integer (In serpent64, integers are 50 bits, two's complement, including the sign bit)

Real -- a 64-bit IEEE double-precision floating point number

String -- an immutable 8-bit (unicode in the future) character string. Characters are represented by strings of length one.

Symbol -- an immutable unique string with an associated global value and global function File -- a handle for an open file

and the following structured types:

Array -- a sequence of values of any type Dictionary -- an associative array

Object -- an instance of a user-defined class

and the following types that users ordinarily don't think of as types: Class -- a user-defined class

Frame -- a stack frame

Method -- a function implementation Thread -- a thread (coroutine)

There are several other types used internally that are not visible to programmers. There is no Boolean type. Instead, the special value nil represents false, and the symbol t represents true. The global variables true and false are bound to t and nil and should be used for readability.

# Syntax

Serpent syntax, like that of Python, uses indentation to indicate structure. Statements are grouped, not by brackets, but by indenting them to the same level, each statement on a separate line.

Generally, statements may be combined on one line by separating them with a semicolon. If two or more statements are separated by a semicolon, all statements are considered to have the same indentation level as the first one.

Certain control constructs may include statements on the same line after the colon rather than indented on the next line. These are def, if, elif, else, for, and while.

# Expressions

## Expressions Denoting Constants

Integer constants are normally familiar strings of decimal digits. However, if the first digit is zero ("0"), the digit string is interpreted as octal and must not contain "8" or "9". A hexidecimal constant begins with "0x" or "0X" and uses "a"-"f" (or capitals "A"-"F") as digits beyond "9".

Real constants are decimal numbers with a decimal point, e.g. "56" is an Integer while "56." is a Real. Reals can also have an exponent suffix denoted by "e" or "E" followed by an integer exponent. "4.5e2" means 4.2 times 10 to the power of 2. If an exponent suffix is present, the decimal point is optional.

String constants are any character string enclosed in double quote (") characters. Within the string, two double quote characters ("") represent a single double quote (") character (a single double quote character would terminate the string.) Alternatively, a double quote can be inserted into a string by escaping it with a backslash character (\). The backslash character is used with other characters to denote special characters in strings:

"\a" denotes audible bell (ASCII code 7),

"\b" denotes the backspace character (ASCII code 8), "\f" denotes the form feed character (ASCII code 12), "\n" denotes the newline character (ASCII code 10),

"\r" denotes the carriage return character (ASCII code 13),

"\t" denotes the tab character (ASCII code 9),

"\v" denotes vertical tab (ASCII code 11),

"\\" denotes backslash (note that a single backslash does not denote a backslash character),

"\'" denotes the single quote character (ASCII code 39),

"\"" denotes the double quote character (ASCII code 34),

"\123" denotes the octal code 123 (any 3 octal digits are permitted, only the low-order 8 bits are used). An invalid UTF-8 tring may result and cause problems with other functions, "\x1A" or "\x1a" denotes the hex code 1A (any 2 hex digits are permitted). An invalid UTF-8 string may result and cause problems with other functions,

"\uxxxx" denotes a Unicode character with the code point given by 4 hex digits (not to be confused with the UTF-8 encoding of that code point),

"\Uxxxxxxxx" denotes a Unicode character with the code point given by 8 hex digits (not to be confused with the UTF-8 encoding of that code point).

The backslash character before other characters denotes that same character, thus "\c" is equivalent to "c".

There is no character type in Serpent. Instead, characters are represented by strings of length 1.

Symbols are unique strings. Each symbol is stored in a system dictionary, and symbols are associated with a global value and a global function. Thus, every symbol is automatically a global variable that can be assigned to, and global variables are declared merely by being mentioned in the program. Symbol constants are like strings, but single quotes are used as delimiters. The same escape codes are valid. Thus, although not recommended, symbols can contain double quotes (no backslash is necessary for escaping this) and even single quotes can be inserted using the backslash,

e.g. 'symbol\'with\'single\'quotes'.

## Expressions for Arrays and Dictionaries

An array is denoted by a comma-separated list of expressions delimited by square brackets, e.g. [1, 'a', "hi"] evaluates to an array with an Integer, Symbol, and String element (in that order). Array expressions are constructed at run time (unlike in Python) because the result is mutable. Therefore, if your program needs a large constant array, e.g. a look-up table, you should construct it once and assign it to a global variable. Then, at the point where the array is used, use the global variable to avoid recreating the table each time you need to use it.

A dictionary is denoted by a list of key/value pairs within curly braces, e.g. {'top': 50, 'bottom': 100, 'left': 10, 'right': 90}. Note that the key/value pairs are separated by commas, and a colon separates each key from its corresponding value. Also note that keys are expressions that are evaluated; without the quotes, a symbol such as 'top' would be evaluated as a global variable named 'top' and raise an error if not initialized.

## Array (or List) Comprehensions

The simple syntax of square brackets containing values is extended to support “list comprehensions.” Specifically, each element in the comma-separated list can be an expression followed by a for clause and an optional if clause. In that case, the for clause (defined below) is executed, and for each iteration, the expression is evaluated to become the next element of the array. (So this is more of an “array comprehension,” than a “list comprehension” unless you call dynamic arrays “lists” as does Python.) In addition, the for clause can be followed by an if clause, in which case the if condition is evaluated on each iteration, and only when true is the expression evaluated and appended to the array. A for clause takes any of the forms of for statements (see Section “Iteration” below), only the clause is in-line (not on a separate line) and is never terminated

with a colon. An if clause is simply the keyword if followed by an expression (the condition). For example, the following constructs a list of integers from 0 through 9:

[i for i = 0 to 10]

The following constructs a list of factors of 144:

[i for i = 1 to 145 if 144 % i == 0]

The following constructs a list of symbols from a list of strings:

[intern(s) for s in ["string1", "string2"]]

The following illustrates the feature that multiple elements can have for clauses. This expression evaluates to an array with integers from 0 to 9 followed by even integers from 10 through 18:

[i for i = 0 to 10, i for i = 10 to 20 by 2]

Finally, the comprehension expressions are just expressions, so they may be nested. The following constructs an array of arrays of increasing length:

[[i for i = 0 to n] for n = 5 to 10]

## Expressions Using Operators

Serpent expressions use the following operators, listed in order of precedence:

., [], **

(unary) +, (unary) -, ~, not

*, /, %, &

+, -, |, ^, <<, >>

<, <=, ==, !=, >, >=, is, is not, in, not in and

or

if else

This last "if else" "operator" is used in expressions of the form expr1 if condition else expr2. The condition is evaluated first. If it is true, the first expression is evaluated to form the value of the overall if else expression; otherwise, the second expression is evaluated to form the value.

Other expressions are formed by calling methods and functions. Parameters are passed by value, and functions may have optional, keyword, and arbitrary numbers of parameters. Keyword parameters are passed by writing the keyword followed by "=", as in:

foo(size = 23)

Only parameters declared as keyword or dictionary parameters can be passed using the keyword notation. All other parameters are positional.

Any expression can be used as a statement.

# Statements

Statements should be familiar to programmers, so they will be described here by example and at most a few comments. Expressions can serve as statements.

## Load and Require

The "load" and "require" statements load a file, executing each statement and compiling each function and class sequentially in the order read from the file. The file may contain its own "load" and "require" statements, which may be immediate commands at the top level or run-time load commands excuted within a function or method. The standard file extension is appended to the filename if no file is found without the extension.

load "myfile" require "myfile"

The difference between load and require is that load always compiles and executes the contents of the file, whereas require first checks to see if the file has been loaded (or "required") previously. If so, the file is not loaded again. Use load when the file contains a script of actions that may be performed multiple times. Use require for files that contain class and function definitions that should be loaded at most one time.

A search path is used to locate source files. Under Windows, the search path is stored in the registry as the SERPENTPATH value in HKEY_LOCAL_MACHINE/SOFTWARE/CMU/Serpent. Under Linux and Mac OS X, the environment variable SERPENTPATH holds the search path.

The search path is a list of paths separated by colons (:) in Linux or OS X or by semicolons (;) in Windows.

Please read these  for more details on setting up a search path.

The search for a file begins by testing the supplied filename for a ".srp" suffix. If none is found, ".srp" is appended to the filename. Then the compiler tries to open the file in the load directory. The load directory is current directory at the time Serpent was started, or, if an initial file was specified on the command line, the directory of that file. If the file is not found in the load directory, the file is searched for sequentially in each directory in the search path until the file is found.

A list of loaded files is kept in an array bound to the global variable files_loaded. The only the filenames with extensions are stored here. Therefore, when a require command is executed, Serpent can check to see if the file has been loaded without appending each path from the search path.

A list (array) of path names of the currently loading files is kept on the global variable paths_currently_loading. When a nested load begins, the new path is appended to the array, and when the load completes, the path is popped from the end of the array. An empty array indicates that no load is in progress.

## Assignment

identifier = expression an_array[index] = expression

a_dictionary[key] = expression an_object.field_name = expression

Assignments may be followed by semicolon (;), and if there is a trailing semicolon, another statement may follow on the same line. Putting a statement after a semicolon is equivalent to putting the statement on the next line at the same indentation level as the current line.

## Conditional

if condition1: stmt1 stmt2

elif condition2: stmt3

stmt4

else:

stmt5 stmt6

Colons are optional. If colons are present, one or more semicolon-separated statements may follow a colon on the same line. If there is at least one statement after a colon, there must not be an indented statement on the next line.

## Iteration

There are three forms of iteration constructs, starting with the familiar "while":

while condition: stmt1

stmt2

The rules for colon and statements on the same line as the colon introduced above for

if-elif-else also apply to while.

In the first "for loop" form, the "variable" may already be declared as a local variable. If not, a local variable is declared (so a subsequent local declaration is not allowed). The "by" part is optional and defaults to 1. The variable is initialized to the value of expression1. The direction (up or down) depends on the value of expression3 (zero or positive is "up", negative is "down"). For the "up" case, the loop exits if expression1 is greater than or equal to expression2. For the "down" case, the loop exits if expression1 is less than or equal to expression2. (Expression2 is evaluated only one time.) If the loop does not exit, the statements are evaluated in sequence. Then expression3 (which is only evaluated once) is added to variable. This cycle of test, execute statements, and add is repeated until the loop exits. It is not an error if expression3 is zero.

Note that "for i = 0 to 4" loops 4 times with i equal to 0, 1, 2, 3, while "for i = 4 to 0 by -1" sets i to 4, 3, 2, 1. Thus, iterating the indexes of an array in the forward direction is accomplished in a straightforward fashion: "for i = 0 to len(the_array)" while iterating in the reverse direction is not so obvious: "for i = len(the_array) - 1 to -1 by -1."

for variable = expression1 to expression2 by expression3: stmt1

stmt2

In the second "for loop" form, "expression1" must evaluate to an array, and "variable" is bound to each value in the array, and "index" is bound to the index of "variable" in "expression1". The "at" part is optional, in which case the index or loop interation count is not available unless you add extra code to track it.

for variable at index in expression1: stmt1

stmt2

At present, there are no equivalents to C's "break" and "continue" statements, but these may be added in the future. An alternative to "break" is to put the loop in a function and return rather than break. An alternative to "continue" is to put the rest of the loop body (that would be skipped by "continue") in a conditional ("if") construct.

The rules for colon and statements on the same line as the colon introduced above for if-elif-else

and while also apply to for.

## Display

display label, expr1, expr2, expr3

The display statement is very handy for debugging and similar to the print statement. The “label,” which should be a quoted string, is printed followed by a colon. Each expression is printed twice, first as if it were quoted, folllowed by an equal sign, and second as if it were an ordinary expression that is evaluated to yield a value. Expressions are separated by commas. For example,

display "in my_sort", x, y

might print:

in my-sort: x = 1, y = foo

If the statement is followed by a comma (,) a comma is printed rather than a newline. A display statement, with or without a trailing comma, may be followed by a semicolon and another statement on the same line.

## Print

print expr1, expr2, expr3; expr4

The print statement writes characters to the standard output, which is the file whose handle is the value of global variable stdout. Each expression is printed, using the equivalent of str(expr) to convert an expression to a string if it is not a string already. A comma outputs one space while a semicolon outputs no space. If there is no trailing comma or semicolon, a newline is output after the last expression in the print statement. A print statement has the value nil.

Because a trailing semicolon is meaningful for formatting, a semicolon (;) after print is used as a format specification. If there are a comma followed by semicolon or two consecutive semicolons (with or without spaces), the first character (comma or semicolon) is a formatting character (so no newline is printed), and the final semicolon terminates the statement, allowing (optionally) another statement to follow on the same line.

## Return

return expression

The expression is optional; nil is returned if no expression is provided.

## Exceptions

There is no exception mechanism, but one may be added in the future.

# Declarations

Serpent functions and classes are created by declaration. Within classes, member variables and methods are declared. Within functions, local variables are declared. Global variables do not need to be declared. Symbols and global variables are equivalent: every symbol has a slot to hold the value of a global, and every global is implemented by creating a symbol.

## Parameter Lists

Simple, positional parameters are declared in the parameter list by simply naming them with comma separators:

def foo(p1, p2, p3):

Parameters can also be specified as required (standard positional parameters), optional (the parameter can be omitted, a default value can be provided), keyword (the formal parameter is named by the caller, the parameter may have a default value), rest (there can only be one "rest" parameter; it is initialized to an array containing the value of all left-over actual positional parameters), and dictionary (there can only be one "dictionary" parameter; it is initialized to a dictionary containing the values of all left-over keyword parameters).

def bar(p0, required p1, optional p2 = 5, keyword p3 = 6, rest p4, dictionary p5):

This function could be called by, for example:

bar(1, p3 = 3, d1 = 4), or

bar(1, 2, 3, 4, 5)

For optional and keyword parameters, a default value may be provided. The syntax is "= expr" where expr is either a constant (a number, a string, or a symbol) or a global variable identifier. If the value is a global variable identifier, the value of that variable at compile time is used. If the value changes at run-time, this will have no effect on the default parameter value. The expr may not be an expression involving functions or operators.

Formal parameters must be declared in the order: required, optional, keyword, rest, dictionary.

The body of the function can be a statement list after the colon (:), statements being separated by semicolons. If there are no statements on the same line, the colon is optional.

## Functions

def foo(p1, p2, p3): var x

stmt1

stmt2

return expression

Functions return the value of the last statement if there is no return statement. Remember that statements may be expressions, allowing a functional style:

def add1(x): x + 1

## Local Variables

As shown above, local variables are declared using "var". Locals may be initialized, and multiple locals can be declared with a single "var" declaration. The declaration may occur anywhere in the function, but it must occur before the first use of the variable.

var x = 1, y = 2

## Classes

class myclass(superclass): var instance_var

def method1(p1): instance_var = p1

Classes specify instance variables (without initialization) and methods, which look just like function declarations except they are nested within the "class" construct. A class may inherit from one superclass. All instance variables and methods are inherited and fully accessible from within or from outside the class.

Within a method, the keyword this refers to the object. You can call methods in the class by writing this.some_method(some_parameter), but you can also simply write some_method(some_parameter), and if some_method is defined in the class or inherited from a superclass, it will override any global function by the same name and will be invoked as a method on this.

To create an object of the class, use the class name as a constructor:

x = myclass(5)

When an object is created, the init method, if any, is called, and parameters provided at object creation are passed to init. (init may be inherited from a superclass). The init method return value is ignored, so it is not necessary to explicitly return this. Within the init method of a subclass, there should ordinarily be a call to initialize the superclass. The special variable super refers to the new object being instantiated as if it were an instance of the superclass. (In the same way that this refers to the current object in the current class, super refers to the current object in the superclass). To call the superclass's initialization method use ordinary method invocation syntax and with parameters appropriate to the superclass's init method. For example, if the superclass is myclass, and the init method of myclass takes one argument, then there should be a call that looks like super.init(5). The return value of this call should be ignored.

Member variables may be accessed directly using "." as in x.instance_var. Methods are invoked in a similar fashion: x.some_method(parameters).

Methods defined for a class can have the same name as methods in a superclass. These methods will override the superclass methods. You can access inherited methods (even ones that are overridden by methods defined in the current class) by refering to the current object as super. Thus

super.meth(parameters) will search for meth starting in the superclass method dictionary, ignoring any definition of meth in the current class. (This is just a more general view of the "trick" used to call a superclass's init method explained above.)

# Debugging

Debugging in Serpent uses compiler messages, run-time error messages, a built-in debugger, and most of all, print statements. Serpent has a very fast compiler, so when an error is encountered, the compiler simply stops compiling and prints an error message. The error message tells you a file name and line number and possibly more. The line number reflects where the error was detected as the file was sequentially processed. The location of the actual error may be before the location where an error is detected.

Run-time error messages occur for many reasons: attempting to access an uninitialized global variable, dividing by zero, an out-of-bounds array index, passing too many or too few parameters to a function, type errors such as using a string where a number is required, etc. When a run-time error occurs, an error message is printed. A line number is printed, but it corresponds to the location of the next instruction. The location of the error may be an earlier line. For example, if the error message reports an array access problem at line 30, but there is no indexing, e.g. "[expr]" on line 30, you should look backwards for an expression with indexing.

The debugger is very simpler, but very useful. Every program should say:

require "debug"

The debugger is just Serpent code. The main limitations are that the debugger cannot single-step or set breakpoints. Instead the debugger is invoked when a run-time error occurs. The debugger can then print out a stack trace (most useful), print the values of local variables, move up and down the stack to examine variables in different stack frames, and resume execution. Type RETURN for a brief summary of commands.

Under wxSerpent, if the debugger is started, it will prompt for input in a pop-up dialog box, which may be confusing. See “” in the wxSerpent page for special considerations when running wxSerpent.

The most useful debugging tools are print and display. Do not be afraid to put display statements in Serpent library programs to help understand how they work. The display command was especially created for quick debugging output.

## Breakpoints

If you required "debug" in you program, you can call breakpoint(1) anywhere in your program. When this call is executed, the debugger will run as if an error occurred, but you can resume by typing ">". The parameter can be any integer to break on the nth call, or if not an integer, then break occurs on non-nil values so you can use a conditional expression to decide when to break.

Each place where breakpoint is called in the source code has a separate counter.

## More Detail

You can tell the debugger to run some code when you exit if you need to clean up something, and you can make stack trace printing optional. See comments in serpent/lib/debug.srp.

# Preprocessing

While not offering a full macro preprocessor, Serpent has some useful features for enabling and disabling code, especially for implementing multiple versions (such as a debugging version).

## Conditional Compilation

The compiler can be directed to skip text using directives that generally work like Serpent’s if, elif and else keywords, except grouping is not based on indentation but rather on a closing #endif directive, and since this operates at compile time, there is no requirement for branches not taken to even compile; thus, you can direct the compiler to skip blocks of documentation or other text. The format is:

#ifdef symbol

...any text... #elifdef symbol

...any text... #else

...any text... #endif

where the # directives must appear in the first column and symbol is any Serpent variable name. Unlike a Serpent conditional that tests an expression for true or false, this tests if symbols are bound to any value. Being unbound (unassigned) is treated as false, and is not an error.

There are a number of other compiler directives.

#if expression

and

#elif expression

evaluate expression at the point in compilation where the directive is reached and either processes or skips the immediately following text.

and

#ifndef symbol

#elifndef symbol

are similar to #ifdef and #elifdef except they test if symbol is not bound.

Sometimes, it is useful to disable debugging, testing, or logging functions in production code while leaving the function calls in place for possible use in the future. Of course you can do this with tests at runtime, but Serpent has a way to eliminate even this overhead by declaring functions to be "no ops":

#noop symbol

declares symbol to be a function that does nothing. Subsequent calls to symbol encountered by the compiler will not result in any parameter evaluation or function call, thus no-op function calls can only be compiled as statements. A no-op function call within an expression has no return value and thus will not compile.

A function definition (def) is ignored if the function name has been declared with #noop.

In Serpent, if there is no return statement, the function return value is the value of the last expression evaluated. This still applies with no-op functions. Consider the following:

// #noop bar def bar(): 1 def foo():

2

bar()

Note that foo() normally returns 1, but if we uncomment the #noop directive, then foo() will return 2 because bar() is not evaluated. (It is not even compiled.)

You can reinstate a no-op function name with the directive:

#yesop symbol

although this could make code very difficult to read and should be used with caution. Even after #yesop, the reinstated function may need to be compiled, and all functions calling it need to be recompiled as well.

# Program Style

Here are some suggestions for Serpent programming style.

## Spaces and Indentation

Indent with 4 spaces. Tell your editor to insert 4 spaces rather than TAB characters. Never use TAB characters because they are invisible and editors treat them differently. See serpent/extras for Sublime and Emacs support files.

Use spaces around all operators: x = a + b / c, not x=a+b/c or even x = a + b/c. Use space after commas to separate parameters: f(x, y, z + 3), not f(x,y,z + 3).

Use blank lines carefully. With longer functions, blank lines can be used to separate logical blocks of code. Often you will want to put a one-line comment at the beginning of such blocks to describe what the block does:

// create a new named widget var w = Widget(name) widget_table[name] = w

// add the widget to the display display_list.add(w) display_list.update_layout()

Since functions and methods have embedded blank lines, it is best to use at least two blank lines between functions and methods. If methods are separated by double-spaces, perhaps classes and function definitions at the top level should be separated by three blank lines. (This can look too spread out; if it does not help readability, less space often looks better.)

And speaking of comments, use a space after comment tokens:

// good comment with space after "//"

//do not run comments into "//" # another good comment

#this comment is missing a leading space

Both "//" and "#" are acceptable comment tokens. Since "#" is darker, I prefer to use it sparingly and sometimes to call attention to important points or key 1-line summaries of functions.

## Long Lines

Limit line lengths to 80 characters. To write long literal strings, just break the line and use + to join them:

"Pretend this is a very long string of text that requires two lines."

could be written as:

"Pretend this is a very long string " + "of text that requires two lines."

Long lines also occur in print statements. You can use a trailing comma or semicolon to avoid printing a newline, then continue printing with another print statement:

print "Imagine that this statement is too long for one line", var1, var2

This can be rewritten as:

print "Imagine that this statement is too long for one line", print	var1, var2

Note that the 2nd print, which is logically part of the same output, had 5 spaces after print so that the data to be printed is indented relative to that of the first print statement. (You cannot indent print itself, so this is a way to show subordinate information or a continuation of the first print statement.) Similarly, display statements have a trick for long lines:

display "Imagine this is too long for one line", var1, var2

If a display statement ends in a comma, no newline is printed. If a display statement does not begin with a literal string, it will not generate an initial label from the string, so the following can be used to break the statement into two lines:

display "Imagine this is too long for one line", display	var1, var2

and the output will be something like:

Imagine this is too long for one line: var1 = 1, var2 = 2

Again, extra spaces help the reader understand the continuation. Of course, it can be inconvenient to produce very long output lines as well. If you have one message to output across multiple lines, you can indent lines after the first, e.g.

print "Imagine that this statement is too long for one line" print "	"; var1, var2

which will print something like:

Imagine that this statement is too long for one line 1 2

With display you more-or-less have to use the initial label, but it can be blank, as in:

display "Imagine this is too long for one line", var1 display "	", var2

and the output will be something like:

Imagine this is too long for one line: var1 = 1

: var2 = 2

## Comments

Unlike Python, Serpent comments can begin with // or #. Always follow // or # with a single space before the comment (or multiple spaces if you want to form an indented block of text.) In the author's opinion, // is prettier than and preferable to #. You can use #, which is darker, for emphasis, e.g. to mark code that needs attention or to provide a one-line summary of each function. Full-line comments should generally precede the thing commented on, and end-of-line comments should follow the thing commented on, e.g.

// pr_range - return integer from low through high - 1 def pr_range(low, optional high)

int(pr_unif(low, high)) // truncate real value

## Names and Capitalization

Variable, class, and function names should be descriptive. It is worth a minute to globally rename variables and naming conventions if it makes your code more readable and consistent!

If you want to be consistent with Serpent libraries, use underscores for multi-word variable names,

e.g. file_length, and use lower-case everywhere except to capitalize classes, e.g. Labeled_slider. Use all-caps for global “constants,” e.g. NOTE_ON = 0x90.

If you must use “CamelCase,” at least start with lower case for variables and functions, and upper case for classes, e.g. var fileLength and class LabeledSlider.

## Telling Stories

The best advice I can give to programmers (and the hardest to learn) is that programs need a semi- formal explanation of how the actual code works. Comments should contain arguments for the correctness of the code. This becomes critical when others (or even you after enough time has passed) try to understand your code. Usually, this happens in the context of something not working. Questions always arise: Did I pass the right arguments? Is the code supposed to handle this edge case? Is the algorithm correct? Is the algorithm implemented correctly? How can the poor reader or user begin to understand if the code is correct without knowing what the code is intended to do or how it is intended to work?

Therefore, programs should have a very careful explanation of the implementation and an argument that the implementation will work correctly. I often write this first before any code, and often spend as much time maintaining the comments as the code. Put the high-level explanation at the top of the program. A similar treatment, on a smaller scale, can be given to each function by putting a block of comments just before the function.

# Weak References

Serpent supports weak references. A weak reference is a built-in object that refers to any heap- allocated object (an Object, a long String, an Array, a Dict or a File). Note that short strings are not heap-allocated so you cannot form a weak reference to just any string. To create a weak reference, use weak_reference = wkrf_create(obj). To access the object from the weak reference, use

wkrf_deref(weak_reference). This will return nil if the original obj has been garbage collected.

# Built-in Functions and Methods

Most built-in functions and methods are known to the compiler, which checks and enforces the parameter counts and translates calls to efficient virtual machine instructions. You can define methods with matching names, but the number of parameters must match. The implementation may assume the "object" for some built-in methods is an array, file, or string. This is an implementation restriction that should be corrected.

## Functions and Methods by Category

### Math

* *, a bs, a tan2, c os, e xp, i div, i nrange, i nt, i seven, i snegative, i sodd, i spositive, l og, pow, r eal,

w ithin, m

ax, m

in, r andom, r andom_seed, r em, r ound, s in, s qrt, t an, i szero

### Logical (Bit) Operations

&

### Strings

, ^ , ~ , |, < <, > >

c hr, c odepoints, c ount, f ind, f romcodepoints, h ash, h ex, i nsert, i nt, i salnum, i salpha, i sdigit, i slower, i sspace, i supper, l ast, l en, o ct, n fkc, o rd, r epr, r everse, s et_len, s tr, s trcat, s ubseq,

t olower, t otitle, t oupper, u ninsert

### Arrays

(create new) a rray, i sarray, a ppend, c lear, c opy, c ount, f latten, i ndex, i nsert, l ast, l en, s et_len, r everse, s ort, r esort, r emove, s ubseq, u nappend, u ninsert

### Dictionaries

c lear, (create new) d ict(ionary), i sdict, get, h as_key, k eys, v alues

### File Operations

c lose, c losed, getcwd, d isplay, f lush, f ileno, i sdir, l istdir, m

kdir, m

ode, n ame open, print, r ead,

r eadline, r eadlines, r eadvalue, r ename, r mdir, s eek, s et_real_format_precision,

s et_real_format_type tell, t oken, u nlink, u nread, w

### System Functions

rite, w

ritelines

getenv, get_os, system, t ime_date, getfeatures, gc_cycles

### Objects, Symbols and Types

i d, i ntern, i sarray, i sdict, i satom, i sinstance, i sinteger, i sinteger, i snull, i snumber, i sobject, i sreal, i ssubclass, i ssymbol, i sstring, s izeof, type, get_slot, s et_slot, symbol_value,

s et_symbol_value, w

### Functions and Methods

krf_create, w

krf_deref

f uncall, a pply, s end, s endapply

### Threads

f ork, join, jointo, r esume, s uspend, yield, yieldto, t hrloc, t hreadid

### Debugging and Other Commands

d bg_cycles, d bg_gc_watch, d bg_end, d isplay, e rror, e xit, f rame_class, f rame_get, f rame_method, f rame_object, f rame_pc, f rame_file, f rame_char, f rame_previous, f rame_variables, o bject_class, o bject_variables, r untime_exception,

r untime_exception_nesting, t race

## Built-in Functions and Methods

abs(x)

absolute value of integer or float

x & y

bitwise and of x and y (two integers)

s.append(x)

extend sequence s (an array or string) by element x; note: use + operator to append two sequences; if s is a string, it is not modified but a new string is constructed

apply(function, argarray)

call function (a symbol) with arguments taken from an array (there is no provision for sending keyword or dictionary parameters in this way)

array(n, fill)

create array of length n, each element initialized to fill, which is optional and defaults to nil. Note that if fill is an array or dictionary or object, the identical object reference is stored at each array location, so any update to one array location will affect all others. If you want an array of objects, consider comprehensions to construct arrays, e.g. instead of array(10, array(10, 0)) to construct a (defective) 10x10 array, use [array(10, 0) for i = 0 to 10]. This executes the expression array(10, 0) 10 times to make 10 separate rows.

atan2(y, x)

compute the arctan(y/x): convert Cartesian coordinates to an angle

chr(i)

convert i, an integer code point (character code), to a one-character string; if i is 0, the string is empty

a.clear()

remove all items from a, a dictionary or array

f.close()

close a file

f.closed()

boolean status

codepoints(s)

convert a string to an array of integer code point values.

a.copy()

shallow copy of a

cos(x)

cosine of x, a float

s.count(x)

count x's in s

getcwd()

return current working directory name

dbg_gc_watch(x)

Turns on debugging information in garbage collector for address x. Only one address may be watched. This only has an effect when Serpent is compiled with the flag _GCDEBUG. Note that x is an integer. See i d.

dbg_cycles()

Returns an integer cycle counter that counts the number of Serpent instructions interpreted. dbg_end()

End debugging and unwind the execution stack. Similar to error(), except that the debugger (if any) is not invoked. This should only be executed by a debugger to escape back to the top level command prompt.

dict(n)

create an empty dictionary expected to grow to size n (n is a hint)

error(s)

generate a run-time error with message s. This normally invokes the debugger.

x ^ y

bitwise exclusive or of x and y (two integers)

exit([i])

stop execution, returning the exit code i if one is provided.

exp(x)

natural exponent of x, a float

f.fileno()

file number

find(string, pattern [, start [, end])

search the substring of string from start to end-1 (inclusive) for pattern. Default is to use the entire string. The match must include all of pattern, in which case the offset of pattern within string is returned; otherwise no match returns -1.

fromcodepoints(array)

convert an array of integers into a string. Any array elements that are not integers or not code points are simply skipped. The resulting string is in normalized in NFKC form. (see

i scodepoints.) flatten(array)

convert array of strings to one string

f.flush()

flush a file

fork()

create a thread (a coroutine). This function forks the current thread into two. A reference to the new thread is returned from fork to the original caller, and nil is returned as if fork was also called by the new thread. The new thread will have a shallow copy of the current stack frame; thus, it inherits all local variables by value (and if a local variable has a dictionary or array, these values are shared with the original thread.) When the new thread encounters a return statement or the end of the method or routine that called fork, the new thread is deleted.

frame_class(frame)

class of the method of the frame.

frame_object(frame)

object (i.e. target or this) of the method of the frame. The result is nil if the method is a global function.

frame_get()

get current frame.

frame_method(frame)

method name of frame

frame_pc(frame)

program counter of frame

frame_file(frame)

source file of frame. This string names the file containing the source code for the current function or method.

frame_char(frame)

source code character index of program counter. This is the source code location of the current instruction, measured as a character offset from the beginning of the source file (see frame_file()).

frame_previous(frame)

return previous stack frame

frame_variables(frame)

return dictionary of variables and their values

funcall(function, arg1, arg2, ...)

call function (a symbol) with arguments

gc_cycles()

return the number of completed garbage collection cycles. Serpent uses an incremental mark- sweep algorithm (not generational scavaging). The number of cycles is incremented at the end of each sweep phase, after which another mark phase begins. Garbage collection runs every INSTRUCTIONS_PER_GC_POLL = 200 Serpent virtual machine instructions and runs for about 1/2 msec on slow machines. The numbers are designed to avoid a big heap and to keep the GC overhead more-or-less constant, avoiding bursts of activity that would interfere with real-time performance.

et(k [, f])

gets item in a with key k (f is returned if no item found, nil is returned if no f is given)

getenv(key)

get the environment value for string key; returns a string

getfeatures()

return an integer detailing options in this version. The integer is the logical or of applicable options: OPTION_WXS (wxwidgets based graphical user interface functions are available), OPTION_ZEROMQ (zeromq functions are available), OPTION_OSC (open sound control functions are available), OPTION_MIDI (portmidi functions are available), OPTION_NETWORK (network functions for TCP-based connections are available), OPTION_SHFILE (Windows shfile library, e.g. for recursively copying directories, is available), OPTION_PROC (real-time proc functions are available), OPTION_O2 (O2 functions are available).

get_os()

get the operating system type: 'linux', 'mach' (OS X), or 'windows'

get_slot(object, symbol)

get the value of the instance variable named by symbol from object

set_slot(object, symbol, value)

set the instance variable named by symbol in object to value

as_key(k)

t if k is key in a

hash(object)

return a hash value. In the current implementation, hash values are 32 bit unsigned integers. Objects are hashed according to their memory location rather than their content, but strings and numbers are hashed according to their values.

hex(i)

convert int to hex string

id(object)

address of the object or string, or hash of the number or short string. A signed integer. This is slightly faster than h ash, but equal strings may have different id's.

idiv(i, j)

integer division: i divided by j

s.index(x)

index of first x in array s (see find function for string searching), -1 if not found

inrange(x, low, high)

equivalent to (low ≤ x and x ≤ high) s.insert(i, x)

insert x as new ith element of an array or string; if i is negative, insert at len + i; use append

to insert at end of s. If s is an array, one element is inserted. If s is a string, x must be a string and the entire string is inserted.

int(x)

conversion to 64-bit integer from a float (by truncation) or string

intern(string)

convert string to symbol

isalnum(s)

isdigit(s) or isalpha(s)? (Only the first character of s is tested.)

isalpha(s)

is character in A:Z,a:z? (Only the first character of s is tested.)

isarray(a)

is a of type array?

isatom(x)

is x a symbol, nil, integer, or real?

iscodepoints(array)

Checks an array for integer Unicode code points. Returns the index of the first element that is

not a code point. If all elements are code points, returns the length of the array.

isdict(d)

is d of type Dict(ionary)?

isdigit(s)

is character in 0:9? (Only the first character of s is tested.)

isdir(path)

return true iff path names a directory

isinstance(object, class)

is object a direct or indirect instance of class?

isinteger(n)

is n of type integer? (Note that isinteger(3.0) is false because 3.0 is of type real.)

islower(s)

is character in a:z? (Only the first character of s is tested.)

isnull(x)

is x null, equivalent to x == nil isnumber(n)

is n an integer or real?

isobject(obj)

is obj an object (an instance of a class)?

isreal(n)

is n of type real? (Note that isreal(3.0) is true because 3.0 is of type real.)

isspace(s)

is character a space, tab, vertical tab, form feed, carriage return, or newline? (Only the first character of s is tested.)

issubclass(class1, class2)

is class1 a direct or indirect subclass of class2?

isupper(s)

is character in A:Z? (Only the first character of s is tested.)

issymbol(s)

is s a symbol (nil is not a symbol)

isstring(s)

is s of type string?

join()

stop execution until all children threads end. A thread ends when it returns from the procedure where it was created (see f ork). Children threads are threads created by this thread.

jointo(thread)

stop execution until thread ends by returning from the procedure where it was created (see

f ork). a.keys()

keys of dictionary a

s.last()

return last element of s, an array or string

len(s)

length of s, an array, dictionary or string. The length of a dictionary is the number of key/value pairs in the dictionary (thus, len(d) == len(d.keys())).

listdir(path)

Obtain a directory listing of path (a string). The result is an array of strings, or nil if the path does not name a directory.

iseven(x)

predicate: is x even? x must be an integer.

isnegative(x)

predicate: is x negative? x must be a number.

isodd(x)

predicate: is x odd? x must be an integer.

ispositive(x)

predicate: is x positive? x must be a number.

log(x)

natural log of x, a float

max(x, y)

maximum of x and y (two numbers)

min(x, y)

minimum of x and y (two numbers)

mkdir(path)

make the specified directory

ode()

mode string that file was opened with

ame()

path string that file was opened with

~x

the bits of integer x inverted

object_class(obj)

return the/a symbol name of the class of an object. Note that classes may be assigned to variables, e.g. if isinstance(obj, Bar) and you assign Foo = Bar, then 'Foo' and 'Bar' denote the same class, so isinstance(obj, Foo) becomes true. On the other hand, if you assign Bar = nil; Foo = nil, then isinstance(obj, Bar) becomes false, and object_class(obj) will return nil.

object_variables(obj)

return a dictionary containing all instance variables of obj and their values, including all instance variables inherited from superclasses.

oct(i)

convert int to octal string

open(filename, mode)

file open, mode is a string (see fopen() in C stdio library)

x | y

bitwise or of x and y (two integers)

nfkc(s)

convert a string to more comparable form (Unicode NFKC normalization). The result may not appear identical to the source, e.g. the ligature for “ff” will be converted to two Latin “f” letters.

ord(c)

inverse of chr(): returns the integer that is the ascii code for the first character in c, a string; if c is empty, zero is returned

pow(x, y)

x to the power y, x and y are floats

x ** y

x to the power y, x and y are floats

random()

pseudo-random float from [0 to 1). See r andom_seed(). random_seed(i)

initialize the pseudo-random number generator used by r andom() using i, a positive integer.

To avoid getting the same sequence of random numbers normally generated by r andom(), call random_seed(time_date()[0]) or random_seed(int(time_get() * 1000)) or use some other non-deterministic value for the seed.

f.read([size])

read up to at least size (default 4096) bytes from file f. If f is opened in text mode, read returns empty string if end-of-file is reached. If an invalid UTF-8 sequence is found, behavior is not specified. Ideally, valid UTF-8 should be returned up to the point where the next character cannot be decoded. Then the next call should return 'NOTUTF8' (named for the ISO C error code). Subsequent reads will resume at the next convertable character. The read may return more than size bytes, and the read may return less than size UTF-8 characters because they require up to 4 bytes each. In binary mode, read returns an array of zero (on

EOF) or more, but no more than size, bytes (see R

f.readline([size])

aw or Binary File I/O).

read line of characters including newline from f, limit number of bytes to size (default 255). Return nil if end of file is reached. Raises an error if file was opened in binary mode. If an invalid UTF-8 character is encountered, behavior is undefined, but should return characters up to that point as a string. The next call to readline will return the symbol 'NOTUTF8' and the next call will resume reading at the next byte where a UTF-8 character can be decoded.

f.readlines([sizehint])

read lines and return in list (if sizehint is given, then read about that many bytes rather than reading to eof). Long lines (> 255 chars) may be split. Returns an empty list if no bytes remain or file is empty. Raises an error if file was opened in binary mode. If an invalid UTF- 8 character is encountered, behavior is undefined, but should return valid characters up to that point. On the next read, readlines should return 'NOTUTF8', and on the next one, resume reading at the next UTF-8 character. Note: To determine that the whole file is successfully

read, even if there is no size parameter, make another call to read to readlines and check for an empty list.

f.readvalue()

read and parse a constant (integer, real, string, or symbol). Note that dictionaries and arrays are not parsed. Whitespace is skipped. Anything that starts with something other than a digit, a period, a single quote, or a double quote is parsed as a symbol (terminated by whitespace). Returns nil if no value is found. If invalid UTF-8 is encountered, results are not defined, but readvalue should return nil. Raises an error if f was opened in binary mode.

real(x)

conversion to 64-bit double from an integer or string

rem(n, m)

remainder of n divided by m, two integers

a.remove(x)

remove item with key x from dictionary a, or remove first element equal to x from array a

rename(oldpath, newpath)

rename a file. Returns nil on success, or errno on error. errno is system dependent.

repr(object)

machine readable string representation of object

s.resort([f])

if all but the last element of array s are sorted in decreasing order, this will sort s (into decreasing order). Use this function to implement a priority queue. Insert by appending an element and calling resort(). Remove the least element by calling unappend(). The optional function f compares two elements of s (see sort). Elements of s may be arrays, in which case the first element of each array is the sort key.

s.reverse()

reverse order of sequence s, an array or string.

rmdir(path)

remove the directory (if empty) named by path. Returns nil on success, or error code.

round(x[, n])

round x to n digits to the right of the decimal point; returns Real if n > 0, otherwise Integer; n can be negative. Rounding is performed by scaling by 10^n, rounding to an integer, and scaling by 10^-n. Rounding is performed by adding 0.5 to positive numbers or -0.5 to negative numbers, then truncating toward zero. If n is omitted, round x to an integer, and if x is an integer, return x.

resume(thread)

If thread is suspended (not ready to run), move it to the ready-to-run queue and status. The caller continues to run and does not yield to thread. (If you want to yield to thread, simply call yieldto(thread).)

runtime_exception(msg, frame)

This is not a built-in function, but there is an implementation in lib/debug.srp If this function is defined, it is called when a runtime exception occurs. The msg is a text description of the error, and frame is the stack frame for the function or method where the error occurred (see frame_... functions to retrieve the instruction, stack, local variables, etc.)

runtime_exception_nesting()

nesting level of exceptions

f.seek(offset, whence)

position in file (whence = 0 means absolute, 1 means relative, 2 means relative to the end)

send(object, method, arg1, arg2, ...)

invoke method (a symbol) on object with the given arguments

sendapply(object, method, argarray)

invoke method (a symbol) on object with the arguments given in an array (no provision is made for keyword and dictionary parameters)

s.set_len(n)

set the length of array s to n; truncate or append nil as necessary; truncate string s or pad with spaces to make new string of length n

x << n

x shifted n bits left (two integers)

x >> n

x shifted n bits right (two integers)

set_real_format_precision(precision)

set the precision for printing real numbers (doubles). The precision is interpreted as in sprintf in the standard C library. The previous value (an integer) is returned if the parameter is valid; otherwise, nil is returned. The initial value is 6. The precision must be in the range 0 through 99.

set_real_format_type(letter)

set the format type for printing real numbers (doubles). The letter must be one of "e", "g", or "f" and is interpreted as in sprintf in the standard C library. The previous value is returned if letter is valid; otherwise, nil is returned. The initial value is "g".

set_symbol_value(s, v)

set the global value of a symbol s to v.

sin(x)

sine of x, a float

sizeof(object)

size in bytes of actual memory used by object, not counting the reference to the object. Since some objects are stored in the reference, some objects have a size of zero.

s.sort([f])

sort elements of array s in increasing order, or use f (a symbol) to compare using a global function; f(x, y) returns true iff x should be after y in the sorted sequence. Elements of s may be arrays, in which case the first element of each array is the sort key.

sqrt(x)

square root of x, a float

str(value)

string representation of value (not necessarily machine readable). If value is an Object with a to_str() method, the method is invoked. Otherwise, if the object has a to_string() method, it is invoked. If neither method exists, or if to_str() returns nil, a string is generated containing the class name (if found) and the machine address as a unique identifier. The preference for to_str() and the possibility for to_str() to block calls to to_string() allows the class to prioritize a small representation for print and display while still supporting a “full” string representation by calling to_string() explicitly.

WARNING: Be extremely careful to avoid run-time errors in to_str() or to_string()! An error will invoke the debugger, which will probably try to print the object using the same faulty code. Note that if an error occurs in init(), objects may not be fully initialized before to_str() is called. In general, assume all instance variables might be nil or some unexpected type. When using instance variable values to construct a string, consider writing str(instance_var) even if you expect instance_var to be a string already, and if you call a function inside to_str(), make sure the parameters are valid. Another strategy, if you have an elaborate to_string() method, is to also define a simpler to_str() method or just use def to_str(): nil, which will allow any stack trace to use the default representation without calling your code. You can then invoke .to_string() when you want the elaborate string representation, and any errors there will be reported without further problems.

strcat(a, b)

concatenate two strings

subseq(s, start [, end])

a subsequence of string or array, returns a new string or array consisting of elements from start through end-1. The default value for end is len(s). If start and/or end is negative, it is interpreted as len(s)-start or len(s)-end, respectively. E.g. subseq([0,1,2,3],-2,-1] is [2].

suspend(thread)

If thread is ready to run, remove it from the read-to-run queue and status. If thread is the calling (running) thread, there are two cases: (1) if another thread is ready to run, the calling thread yields and then suspends so that another thread will run immediately; (2) if no other thread is ready to run, the calling thread is not suspended and instead continues to run.

symbol_value(s)

get the global value of a symbol.

tan(x)

tangent of x, a float

system(s)

invoke the shell using command s, returning the exit status of the shell (may not be implemented on Windows, see Unix system() for details)

f.tell()

return current position in file

threadid()

Return the current thread. (The "ID" of a thread is a reference to a primitive object of type

'Thread'.) thrloc(thread)

Every thread has a dictionary for thread-specific data. Return the thread-local dictionary for

the given thread. If thread (optional) is omitted, the default value is the current thread.

time_date()

get the time and date as a 12-element array of the form: [seconds (0-60), minutes (0-59), hours (0-23), day-of-the-month (1-31), month-of-year (0-11), year (1900-?), day-of-week (Sunday = 0), day-of-year (0-365), is-summer-time-in-effect? (t or nil), abbreviation-of- timezone-name (e.g. "EST"), offset-from-UTC-in-seconds (positive values indicate locations east of the Prime Meridian)].

f.token()

skip over white space in file f; read string of non-whitespace characters terminated by a whitespace. The maximum token length is 255 characters. Returns empty string on EOF. Raises an error if file is opened as a binary file.

tolower(s)

convert letters to lower case in s

totitle(s)

convert all letters to title case in s. Except for some non-ASCII characters, this is equivalent to toupper. Normally, this would be called to convert individual characters that begin words in a title.

toupper(s)

convert letters to upper case in s

trace(n)

Set trace mode. Bit 0 controls machine tracing: instructions are disassembled and printed as they are executed, and the contents of the stack are displayed. Bit 1 controls compiler tracing: tokens are printed as they are parsed, and other debugging output related to the compiler and code generation are printed.

type(object)

return type of object (a symbol)

s.unappend()

remove and return last element of s, an array

s.uninsert(i [, j])

remove s[i] (through s[j-1]), where s is an array or string.

unlink(filename)

unlink (delete) a file. Returns nil on success, or errno on error. errno is system dependent.

f.unread(c)

push a single character (a string of length 1) back to an input file

a.values()

values of dictionary a

within(x, y, epsilon)

true if x is within epsilon of y (three reals)

wkrf_create(obj)

Create a weak reference to obj. A weak reference stores a reference to obj that is not seen by the garbage collector. Holding the weak reference (which is also a kind of object) will not prevent obj from being deleted. Use wkrf_deref() to retrieve the original reference to obj if it has not been deleted.

wkrf_deref(wkrf)

Retrieve obj from a weak reference wkrf created by wkrf_create(obj). If obj has been freed (deleted) by garbage collection, nil is returned. There is no race condition: if wkrf_deref returns an object reference, then for as long as it exists, the reference will prevent the garbage collection of obj.

f.write(str)

write string to file if file is opened in text mode. Write bytes from an array (str must be of

type Array) if file is opened in binary mode (see R

f.writelines(list)

write strings to file

yield()

aw or Binary File I/O). Returns f.

begin running the next ready-to-run thread; the current thread becomes ready-to-run (waiting to run later). If the current thread is the only one ready, it will continue running.

yieldto(thread)

begin running thread, making the current thread ready to run at a later time. If thread is the current thread, it will continue running.

iszero(x)

predicate: is x zero? x must be a number.

When a built-in operation encounters the wrong types and the first argument is an object, then the call is converted into a method lookup. (This is not implemented for all primitives yet.)

It is illegal to define a global function with the name of a built-in function.

Serpent does not have first-class functions. Instead, functions are represented by symbols (call the corresponding global function). A planned extension is to let objects represent functions. When an object is applied to a parameter list, a special method (possibly 'call') is invoked on the object.

# Special Variables

command_line_arguments

An array of strings from the command line. For example, if your command is

serpent64 myprog.srp 15 xyzzy, then command_line_arguments will be initialized to ["myprog.srp", "15", "xyzzy"]. Note that all elements are strings. When you run serpent64 or wxserpent64 from the command line, you give the name of a Serpent source file as the first command line argument. (The default if "init".) This can be followed by additional arguments. The source file name and additional arguments (but not the Unix command, e.g. "serpent64") are used to initialize command_line_arguments.

dbg_trace_output_disable

In the debug version (compiled with _DEBUG defined), Serpent copies every output byte to the trace() function, a platform dependent debugging output function. If you set this variable to non-nil, this trace output is disabled. This can make the program run faster in debug mode.

files_loaded

An array of files that have been loaded so far. The require statement uses this list to decide whether to load a file.

paths_currently_loading

An array of strings naming the paths of the set of nested loads in progress. If you want to load a file relative to a source file, you should save paths_currently_loading.last() in a statement that is executed while the file is being loaded.

runtime_exception

If defined as a global function, this function will be called by Serpent to handle execution exceptions within Serpent code. See debug.srp, which uses this feature to implement a simple debugger.

stderr

Currently, no built-in functions use this variable; however, it is initialized to the application's standard error file for use by applications.

stdin

Currently, no built-in functions use this variable; however, it is initialized to an input file or virtual file (either console input or string input via a dialog box) for use by applications and the debugger.

stdout

Serpent's print functions write to this file which is initialized to the console output (if available). You can overwrite this variable to redirect output (see also stdlog below). If Serpent expects a valid file here and does not find one, Serpent will overwrite the variable, restoring it to the original value.

stdlog

All print output is duplicated and written to stdlog if this variable is set to an opened (virtual or real) file. In particular, stack traces will be copied here if the debugger is loaded and if dbg_stack_print is true. In fact, the debug.srp library, if loaded, will open "srp.log" and write a stack trace there if stdlog is not already initialized.

# Console, Terminal, or Command Line Input and Output

Now that you found your way to this section, we'll use "terminal" to refer to interfaces based on keyboard input and simple text output. Terminal output is normally accomplished with print and display commands, but you can also use file IO commands. The global variable stdout is initialized to the terminal, so for example, stdout.write("Hello World!\n") is equivalent to print "Hello World!".

There are no special terminal input commands, but you can use stdin to refer to the keyboard, so for example, stdin.readline() will return a line of text. Backspace and other editing characters are processed as you type and are not captured by stdin. Because of the built-in editing, you cannot capture individual keystrokes. Instead, input text becomes readable when you type the <enter> or

<return> key. Consider also stdin.read(1) to read the next character only, and stdin.readvalue()

to read one token at a time, stripping out white space.

If you develop a lot of code that uses print and then decide you would like to redirect the terminal output to a “real” file, you can reassign stdout to a file that is open for writing. Be careful! If you encounter an error, Serpent error messages and debugging output will be written to stdout, so you may not see it. Also, be sure to save the original value of stdout and restore it after redirecting output to a file.

# Raw or Binary File I/O

To open a file for raw binary access, include “b” in the mode parameter, e.g. open("file.raw", "bw") or open("file.raw", "br"). Serpent does not have a special “blob” or byte-string data type, and UTF-8 strings are not valid if they contain certain byte values, so Serpent uses arrays of integers to encode raw binary byte strings. The r ead method returns an array when the file is opened in binary mode, and the w rite method expects an array for files opened for binary write.

To use memory more efficiently, each integer encodes up to 6 bytes, so the byte sequence 1, 2, 3, 4, 5, 6 becomes the integer 0x060504030201. The first element of the array is the byte sequence length (as an Integer >= 0). To access the nth byte of array a, you can write:

((a[1 + idiv(n, 6)] >> ((n % 6) * 8)) & 0xff)

The array methods get_byte(n), set_byte(n, v), append_byte(v) and append_bytes(a) are under consideration as a future extension.

# Standard Libraries

Serpent comes with a number of files in the lib directory, and normally this directory should be on the Serpent search path. Serpent libraries are evolving with use. Feel free to contribute new libraries and methods of general utility. The list below is intended as a rough guide. Please read documentation in the source files themselves for more detail.

debug

Serpent has a primitive debugger. When you load the debug library, errors are passed to some library code that can print a stack trace and examine some variable values. Also, you can exit back to the command line prompt. Type RETURN to the debugger for a summary of commands.

file sets, find files, etc.

The File_set class represents a set of file paths. Find_files is a subclass that can search a directory tree for files that match certain criteria. Find_extensions is a subclass of Find_files that can search a directory tree for files with a certain extension, e.g. ".jpg". The lib/files.srp file has these classes and other handy file and path utilities for manipulating path names.

prob

This file implements a number of functions for random number generation and random selection from lists. Functions include a normal or Gaussian distribution and a Markov chain implementation.

regression

The Regression class can be used to perform (linear) regression. statistics

The Statistics class can be used to perform simple statistics such as mean and standard deviation. It can also buffer a set of statistical samples and save them to a file.

stredit

The String_edit class is intended to edit files, e.g. perform global query-and-replace operations. The original purpose was editing templates to automatically generate HTML as part of the serpent software release process, but any file or string editing might make use of this class.

strparse

The String_parse class is intended to parse data files of all kinds one line at a time. You pass in a string you want to parse, and then sequentially advance through the string skipping spaces, reading words, integers, floats, special characters, or whatever. Highly recommended for all your text input needs.

utils

This is a grab-bag of handy functions, including: irandom to get random integers, uniform to get uniformly distributed real numbers, change_file_suffix to replace a file name suffix, file_from_path to extract the file name from a full path, and pad to pad a string to a given length.

readcsv

This code, currently in programs, not lib, can read comma-separated value files from Excel or other spreadsheets.

# Thread Interface

Serpent threads are unlike Python or Unix threads in that they are non-preemptable, meaning that threads run until a command explicitly allows another thread to run. Only one thread runs at once, even if multiple processors are available.

To create a thread, use fork(), which copies the current stack frame (the current function’s local variables and program counter). The original thread continues executing and the new thread starts executing as if both called fork(). The difference is that in the original thread, fork() returns the new thread (a reference to a thread primitive of type Thread, while in the new thread, fork() returns

nil (false) and when this thread returns from the function where fork() was called, the thread terminates.

After creating a new thread with fork(), the calling thread yields to the new thread. You can also suspend threads to take them off the runnable list so they will not be yielded to (see suspend(), and you can make a suspended thread runnable again (see resume()).

A typical way to create a thread to perform some computation is:

if not fork():

some_computation() // runs on new thread return

... work for main thread continues ...

Alternatively, one can make a function that runs on a separate thread as follows:

def some_computation()

if fork(): // create new thread for the work return // caller does none of the work

... some computation here for new thread ...

One could also arrange things to defer computation until after the main thread suspends or yields control:

def some_computation()

var caller = threadid() // get the calling thread if fork()

return // caller will run this soon after fork()

// after fork, new thread will run immediately,

// so yield control back to calling thread yieldto(caller)

// eventually, control will come back to this new thread:

... some defered computation here for new thread ...

# Procs - Preemptable Thread Interface and Functions

Serpent has two types of threads. “Normal” threads are non-preemptable coroutines that share the heap (thus all globals are common to these threads). You can create as many of these threads as you wish. The second form is limited to one additional thread (called a "process" or "proc" to avoid overloading the term "thread") that loads a file and then periodically calls a function. This proc has an independent heap (thus no variables are shared) and runs at higher priority than the main proc. It can preempt the main proc or run while the main proc is blocked waiting for input or sleeping. The entire preemptive proc interface consists of proc_create(), proc_send() and proc_receive().

All communication between these two procs is through message queues. Two queues are set up and initialized to hold up to 100 strings of up to 100 characters each. Only strings may be sent and received. To build Serpent with these proc functions, link Serpent with the objects obtained from proccreate.cpp and prochack.cpp. (Look for the CMake option USE_PROC to use procs.)

It is strongly recommended that you do not depend heavily on this simple proc interface. It was created to support a course and is not intended for “real” use.

proc_create(period, filename, mempool)

create a new instance of the Serpent virtual machine

allocate an initial memory pool (mempool is a hint for the size of the initial memory pool. It is currently ignored. Future implementations will interpret a value of 0 to indicate the default memory pool size, which is currently 1MB.)

load the file indicated by filename (a string)

set the variable proc_id in the new proc to an integer (see below) return the new proc’s proc_id

Once a new proc is created and it has finished successfully loading/compiling/executing commands from filename, the proc uses PortTime to wake up every period milliseconds and call porttime_callback(ms), where ms is the current time in milliseconds.

proc_send(proc_id, string)

enqueue string for receipt by the other proc. Return the number of strings sent (0 if the queue is full, 1 if the send is successful.) proc_id should be the proc id of the caller, not the destination. (Use the global variable proc_id.

proc_receive(proc_id)

check the queue and if there is a message from the other proc, return the message as a string. If there is no message, "" (the empty string) is returned. Note that it is possible to send an empty string, but this will be indistinguishable from no message (an empty queue). proc_id should be the proc id of the caller, not the proc that sent the message. (Use the global variable proc_id).

# Network Interface and Functions

If Serpent is compiled with NETWORK defined, then some basic communications functions are built-in. They are defined in this section.

server_create(portno)

Create a socket, bind it to portno, and listen for client connections. A socket descriptor (number) is returned. -1 is returned to indicate an error.

server_accept(socket)

Accept a client request on socket, which was created by server_create. If the return value is nil, then no client request is pending (this is a non-blocking call). If the return value is negative, an error occurred. -1 indicates an error was reported from the accept operation. -2 indicates that the socket parameter value is invalid. (Other negative integers should also be treated as errors.) Otherwise, the return value is socket that can be used to read the client request. Under Windows, calling this function initiates a blocking accept call in another thread. In order to call server_connect or socket_receive, you must continue (re)calling server_accept until it returns something other than nil. To terminate the blocked accept, try closing the server socket and then re-calling server_accept to read the error return.

server_connect(name, portno)

Establish a connection with a server using its name and port number. The result is a socket, nil if no result is available yet (this is a non-blocking call), or -1 if there is an error. If nil is returned, you must re-call server_connect until a non-nil result is obtained.

socket_receive(socket, n)

Read up to n bytes of data from socket. Returns a string if successful, nil if no input is available (this is a non-blocking call), and otherwise returns an integer error code. The error code -2 is returned if the socket parameter is invalid. The socket is normally obtained from server_accept or server_connect. If nil is returned, the read is still in progress, and you must re-call socket_receive until a non-nil result is obtained.

socket_send(socket, string)

Send a string to the given socket, which is normally obtained from server_accept or

server_connect. Returns the number of bytes sent or -1 on error.

socket_close(socket)

Close a socket.

# Windows Shell File Operations

The Win32 version of Serpent includes an interface to "Shell File Operations" that perform tasks

such as copying directories. These functions are:

sfo_copy_directory(from_path, to_path)

Copy a directory named by from_path to to_path (both arguments are strings).

sfo_delete(path)

Delete a file or directory named by path (a string).

create_directory(path)

Create a directory named by path (a string).

local_time()

Return the local time as an array of integers, organized as follows: [seconds, minutes, hours, day-of-month, month, year, day-of-week, day-of-year, dst], where dst is 1 for daylight savings time and 0 otherwise.

# O2

Serpent can act as a client, a server, or both, using O2. O2 is intended as a replacement for OSC, so if you compile Serpent with O2, you should probably not add the OSC functions.

Unless otherwise specified, O2 functions return an integer error code which is O2_SUCCESS (= 0) if no errors were detected. The integer can be converted to a readable string using o2_error_to_string().

The functions are:

o2_debug_flags(flags)

Set flags to enable debug message printing within the O2 library. The flags are a string. Options are: (c) basic connection data, (r) non-system incoming messages, (s) non-system outgoing messages, (R) system incoming messages, (S) system outgoing messages, (k) clock synchronization protocol, (d) discovery messages, (h) hub-related activity, (t) user messages dispatched from schedulers, (T) system messages dispatched from schedulers, (l) trace (local) messages to o2_message_deliver (m) memory allocation and free, (o) socket creation and closing, (O) open sound control messages, (q) show MQTT messages, (g) general status info,

(n) all network flags: rRsS, (a) all debug flags except m (malloc/free), (A) all debug flags except malloc and scheduling, (N) disable network if flags are set before o2_initialize() is called. Internal IP becomes 127.0.0.1, public IP is 0.0.0.0 (signifying no Internet connection). Interprocess communication on the host is supported.

o2_network_enable(flag)

Enable (true) or disable (false) the network. Must be called before o2_initialize(). Default is network enabled. See also o2_debug_flags("N").

o2_initialize(application, debug_flag)

Initialize O2. application is a unique string shared by all O2 processes in a distributed O2 application. (You can have multiple O2 applications sharing the same local area network as long as each application uses a different name.) If debug_flag is non-nil, debugging information may be printed. (Exactly what is printed is intentionally not specified.)

o2_get_addresses()

Get the IP addresses and the port used by O2 for this process. An array is returned with three elements: The public IP address as a hexadecimal string, the internal IP address as a hexadecimal string, and the port number as an integer (this is both the TCP and UDP port number. If there is an error, nil is returned.

o2_service_new(service)

Create an O2 service named service, a string parameter.

o2_get_proc_name()

Get the IP addresses and TCP connection port used by O2 for this process. A string is returned of the form "@76543210:a2010011:64541" where the colon separates the IP

addreseses and port number.

o2_services_list()

Take a snapshot of services. Since services can change, you can only query services by taking a snapshot first using this function. Then you can use the following functions to obtain information about services. When you are finished, call o2_services_list_free() to release the data structure (or you can simply leave it – the old snapshot will be freed the next time you call o2_services_list).

o2_services_list_free()

Release current snapshot of services.

o2_service_name(i)

Get the name of the ith service (nil if none).

o2_service_type(i)

Get the type of the ith service. Returns 0 if none, O2_LOCAL (4), O2_REMOTE (5), or O2_TAP (8).

o2_service_process(i)

Get the name of the process offering service i.

o2_service_tapper(i)

Get the tapper for service i (if service i is a tap, otherwise returns nil).

o2_service_properties(i)

Get the properties for service i. The properties string has the format "attr1:value1;attr2:value2;..." where attributes are alphanumeric and values can be any string with backslash (\) used to escape backslash, colon, and semicolon ("\\", "\:", "\;"). A non- empty string will end with ";".

o2_service_getprop(i, attr)

Get the value, a string, of an attribute for service i (if none, returns nil).

o2_service_search(i, attr, pattern)

Starting with service i, search for a service where attribute attr has a value the matches pattern, which can have four forms: ":pre" matches if the value begins with pre. "sub" matches if sub is a substring of the value. "suff;" matches if suff is a suffix of the value and ":exact;" matches if exact exactly matches the value. Remember that value characters may be escaped. E.g. to exactly match value "x;y", the pattern (as a Serpent string, which also needs to escape "\") would be ":x\\;y;". (Moral: avoid using colons and semicolons in values!)

o2_service_set_property(service, attr, value)

Set the value for an attribute in service (all strings).

o2_service_property_free(service, attr)

Remove an attribute from service (both strings).

o2_tap(tappee, tapper, send_mode)

Install a tap on existing service tappee. Messages to tappee are copied and send to tapper. Both tappee and tapper parameters are strings. The send_mode parameter is one of 0 for TAP_KEEP, 1 for TAP_RELIABLE, or 2 for TAP_BEST_EFFFORT. This parameter controls the send mode when messages are tapped. TAP_KEEP means the message is sent to the tapper using the same method (TCP or UDP) as that of the message to the tappee.

o2_untap(tappee, tapper) Remove a tap. o2_service_free(service)

Remove (destroy) an O2 service named service, a string parameter.

o2_method_new(path, types, method, coerce)

After initializing O2, incoming messages will be examined, but only messages that match a registered path result in any action. Use this function to register a path, a string (e.g. "/myservice/slider"). To accept any incoming address to a service, use the service name for path, e.g. "/myservice". In addition to matching path, message types can be checked, and messages that fail the type checks are rejected (dropped). Type checking has three levels: If types is nil, no type checking is performed, and all messages matching path are accepted.

The method is called with: the message timestamp, the message address, the actual type string from the message, and with one argument for each data element in the message. (The type string is not redundant because multiple O2 types such as 'f'loat and 'd'ouble are converted to the same Serpent type (Real.) If types is not nil, it must be a string of O2 type characters.

If coerce is true, then the actual message data elements are coerced to the types given by types, if possible, and the message is delivered by calling method. If coercion is not possible, the message is dropped. Finally, if coerce is false, the message types must match types exactly, in which case method is called with the expected types (saving any further type checking in Serpent); otherwise, the message is dropped. Note that if types is nil (or equivalently, false), you can receive messages of varying numbers of parameters by using the rest keyword in the method parameter list to assemble the multiple parameters into a Serpent array. The parameters passed to the method are timestamp, the O2 message timestamp, address, the address string from the message, types, the type string for the actual parameters, and finally the actual parameters extracted from the message. The types will match types.

o2_method_free(path)

Free the method or subtree of methods corresponding to path.

o2_message_warnings(fnsymbol)

If a message is dropped, call the function named by fnsymbol with a warning message (string) and the path of the message (string) that was dropped.

o2_poll()

O2 does not run in a separate process, so you must call o2_poll() periodically in order for O2 to function. To avoid hogging the CPU and using lots of power, you should probably sleep for at least 1ms between calls to o2_poll(), e.g. call time_sleep(0.001). Reasonable polling periods range from 1ms to 100ms. Timed message delivery happens during o2_poll(), so timing precision is directly related to the polling period.

o2_status(service)

Check the status of an O2 service named service, a string parameter. The return value is an integer code as follows:

O2_BAD_SERVICE_NAME (-16) means service is null, empty, or contains a slash (/) or exclamation point (!).

O2_FAIL (-1) means the service does not exist.

O2_LOCAL_NOTIME (0) means the service exists locally, but clock sync has not been established.

O2_REMOTE_NOTIME (1) means the service exists in another process, but clock sync has not been established.

O2_BRIDGE_NOTIME (2) means the service exists in a bridged process (not yet implemented), but clock sync has not been established.

O2_TO_OSC_NOTIME (3) means the service forwards messages to an OSC server, but clock sync has not been established.

O2_LOCAL (4) means the service exists locally, and clock sync has been established. O2_REMOTE (5) means the service exists in another process, and clock sync has been established.

O2_BRIDGE (6) means the service exists in a bridged process (not yet implemented), and clock sync has not been established.

O2_TO_OSC (7) means the service forwards messages to an OSC server, and clock sync has been established.

o2_can_send(service)

test if a message to service will block. O2 always allows at least one message to be pending and not yet sent, and the kernel is likely to buffer multiple messages. If this call returns O2_SUCCESS, then a send is guaranteed to return quickly. Otherwise, the call might block until the receiver receives more messages. In extreme cases, depending on application design, blocking can cause two communicating processes to deadlock.

o2_roundtrip()

Return an array containing the mean and minimum round trip time to the clock reference. Returns nil if clock synchronization is not achieved.

o2_clock_set()

Set the global O2 clock time to be the local time. Do this in at most one process in an O2 application of distributed processes.

o2_clock_jump(local_time, global_time, adjust)

set the mapping from local time to global time, e.g. when global O2 time jumps. Optionally adjust scheduled message times to retain wall time (if adjust is true)

o2_sched_flush()

flush all pending messages from the O2 scheduler, returns how many were flushed. These would be O2 messages with a timestamp waiting to be delivered. This does not affect Serpent events scheduled with Scheduler or Vscheduler objects.

o2_time_jump_callback

is a global variable set to a callback function name. The callback is called when there are large jumps in O2 reference time. The function parameters are local_time, prior_global_time and new_global_time and it should return true if an action was taken, in particular a call to o2_clock_jump. Otherwise, the time jump simply happens when the call returns or if o2_time_jump_callback is left undefined.

o2_time_get()

Get the O2 global clock time if synchronized

o2_local_time()

Get the local O2 clock time

o2_error_to_string(error)

Convert the (integer) error into a human-readable string, which is the return value.

o2_finish()

Shut down O2 and free resources.

o2_osc_port_new(service, port, tcp_flag)

Create an OSC server that forwards incoming messages to the O2 service named by the string service. The service is offered on the port given by the integer port, and the port will receive messages via UDP unless tcp_flag is non-nil, in which case TCP is used.

o2_osc_port_free(port)

Free the OSC server associated with port, but do not free the service that it forwarded to.

Call

o2_osc_delegate(service, ip, port, tcp_flag)

Create an O2 service, named by the string service, that forwards O2 messages to an OSC server defined by the string ip (IP address or "localhost"), the integer port (port number), and the boolean tcp_flag which specifies whether to connect via UDP or TCP.

o2_send_start()

Prepare to send a message. This should be followed by appending zero or more arguments and then sending to a path using o2_send_finish(). Other sequences of calls to O2 result in undefined behavior. Calls to append parameters are as follows:

o2_add_int32(i)

Append a 32-bit integer argument i to the current message initiated by

o2_send_start(). o2_add_float(x)

Append a float argument x to the current message initiated by o2_send_start(). o2_add_blob(s)

Append a blob argument consisting of bytes in Serpent string s. o2_add_string(s)

Append a string argument s to the current message initiated by o2_send_start(). o2_add_int64(i)

Append a 64-bit integer argument i to the current message initiated by o2_send_start(). Note that Serpent64 integers are 50-bit signed integers, so using all 64 bits is not possible.

o2_add_double(x)

Append a double argument x to the current message initiated by o2_send_start()). o2_add_time(t)

Append a double-precision time t to the current message initiated by o2_send_start().

Note that O2 times differ from OSC timetags even though both use the character "t" as

the type code. Although O2 might convert between these representations, do not expect meaningful information to flow between O2 and OSC through type "t" arguments.

o2_add_symbol(s)

Append a symbol argument s to the current message initiated by o2_send_start(). o2_add_char(c)

Append a character (represented in Serpent by a one-character string) argument c to the

current message initiated by o2_send_start(). o2_add_midi(cmd, d1, d2)

Append a Midi message (represented in Serpent by 3 integers) argument to the current

message initiated by o2_send_start(). Within the O2 message, the message has the OSC representation of a 32-bit int containing (from high- to low-order bytes) port, status, data1 and data2 bytes. The port (not used) is zero.

o2_add_bool(b)

Append a boolean argument b to the current message.

o2_add_nil()

Append a Nil argument to the current message initiated by o2_send_start(). The value passed as actual argument to the message handler is Serpent's nil.

o2_add_infinitum()

Append an "Infinitum" argument to the current message initiated by o2_send_start(). The value passed as actual argument to the message handler is the symbol 'Infinitum'.

o2_add_start_array()

Begin to add an array to the current message initiated by o2_send_start(). This is represented in the type string with the character "[".

o2_add_end_array()

Finish an array in the current message initiated by o2_send_start(). This is represented in the type string with the character "]". The actual argument delivered to the handler will be a Serpent array. Nested arrays are supported. You  might expect o2_add_array(a) so simply take a Serpent array and add the elements to a message.

This is not provided because the types of the elements would be ambiguous (e.g. whether to send float vs. double cannot be determined from Serpent types alone.) However, o2_add_vector() can add homogeneous arrays of numbers.

o2_add_vector(v, type)

Append a vector (a Serpent array of numbers) where element types are given by type which is a string argument containing "i", "h", "f", or "d" for int32, int64, float, or double.

o2_send_finish(time, address, tcp_flag)

Send the constructed message initiated by o2_send_start() with timestamp time to the given address, using TCP if tcp_flag is non-nil, and otherwise UDP. (However, messages within a process are delivered directly without any network transmission.)

o2lite_initialize()

Make this process an O2lite server. O2lite is a simple subset of O2 intended for microcontrollers, web apps, and other clients.

o2_http_initialize(port, root)

Make this process an HTTP server supporting O2lite over web sockets. See ow2s.js for browser-side implementation. The port is the server port number (an integer) and root is prefixed to the URL to form a path to web pages. It can be relative (to the Serpent current directory) or absolute.

o2_mqtt_enable(server, port)

Allow this process to use MQTT. The server and port specify the broker, or use "" and 0 for the defaults, currently "mqtt.eclipseprojects.io" and 1883.

# Open Sound Control

Serpent can act as a client, a server, or both, using O (OSC). There are two

implementations of the OSC functions, and Serpent can be compiled using either (but not both). The original implementation is based on This library is fairly complete, but it calls malloc() to copy messages and strings, which could cause some problems in real-time systems. The newer

implementation (called MinOSC here) is smaller, simpler and faster, but does not implement timed messages, bundles, or arrays. On the other hand, MinOSC was designed to punch through NAT (search for NAT below for more details) and receive from multiple ports. The default implementation is MinOSC. You might want to consider switching to Liblo if you need different functionality.

The functions are:

osc_server_init(port, debug_flag)

Initialize an Open Sound Control server, using the specified port string (e.g. "7770"). If debug_flag is non-nil, debugging information may be printed. (Exactly what is printed is intentionally not specified.) It is an error to open more than one OSC server. On success, OSC_SERVER_SUCCESS (= 0) is returned. Upon failure, an integer error code less than zero is returned. If the OSC server is already initialized and this call is made from the same thread as the initial one, OSC_SERVER_ALREADY_OPEN is returned. However, if an attempt is made to initialize the server from a second thread, an error is raised, stopping execution of the thread and calling the debugger or resetting Serpent to the top level command prompt. The port string may also be the special string "reply", in which case the server will listen to the reply port, which was previously set by a call to osc_send_reply() or automatically generated by the first call to osc_send(), whichever was first.

osc_server_port(port)

Add a port (specified as a string, e.g. "7770") to the set of ports from which the server receives. Returns 0 on success or -1 on failure. The liblo implementation does not support listening on multiple ports and always returns -1.

osc_server_multicast_init(group, port, debug_flag)

Initialize an Open Sound Control server and join a multicast group. Both group and port

parameters are strings. Otherwise, behavior is identical to osc_server_init described above.

osc_server_method(path, types, obj, method)

After initializing the OSC server, incoming messages will be examined, but only messages that match a registered path result in any action. Use this function to register a path, a string (e.g. "/slider"). The types of the arguments are given by types, a string (e.g. "if"). When a message matching path is received, arguments are coerced into the specified types and a handler specified by method is called. If obj is non-nil, it must be an Object with the given method. Otherwise, method is called as a global function. The first method parameter will receive the (string) value of the path parameter. The remaining method parameters must be compatible with types (e.g. either the count matches or method has optional or rest parameters).

osc_server_recv_port()

After receiving a message and method is called, the port from which the message was received can be retrieved with this function. The return value is an integer. The result is only valid if the function is called from within the method that is handling an incoming message.

osc_server_sender_ip()

After receiving a message and method is called, the message sender's IP address can be retrieved with this function. The return value is a string in the form nnn.nnn.nnn.nnn. The result is only valid if the function is called from within the method that is handling an incoming message.

osc_server_poll()

Since Serpent is single-threaded, the server must be explicitly activated by calling this function, which receives all pending messages, parses them, and dispatches any handlers registered using osc_server_method. Normally, 0 is returned, but upon failure, an integer error code less than zero is returned. You should call this function at a rate consistent with the rate of OSC messages and your tolerance for latency.

osc_server_reply()

When an OSC message arrives, it is parsed and passed to a method registered by

osc_server_method(). Within this method, it is possible to access the reply address of the

incoming message by calling osc_server_reply(). There are no parameters, and the result is an integer. If the integer is non-negative, it is an address identifier, compatible with results from osc_create_address() and osc_send(). Otherwise, an error occurred and no address  was found or created. The reason you might want to use a reply address, rather than, say, an agreed-upon IP address and port number, is that if the client is behind a router that uses NAT, the router might change the client's IP address and port number. In this scheme, called Net Address Translation (NAT), the only way to get a message back to the client is to reply. The router will then do the reverse translation on the address to reach the client. osc_server_reply does nothing and returns -1 in the Liblo version.

osc_server_finish()

Close the OSC connection, freeing any resources that were allocated for the server.

osc_create_address(host, port, bind)

Initialize an OSC client to send to a server denoted by the host and port strings. If host is nil, the host is the local host. If bind is true, a bind is performed on the created socket. If this is the first created address and osc_server_init() has not been called, then the OSC server is initialized with this port. This allows the socket to receive messages, and as a side-effect, the port will be added as a reply port to outgoing messages. (See osc_server_reply() above.) The bind parameter is ignored in the Liblo version. Returns an address identifier (a non-negative integer) on success, or a negative integer error code on failure. Note: Serpent can manage only a limited number of addresses, so create an address once and save it for use with osc_send. Do not call osc_create_address every time you call osc_send.

osc_delete_address(n)

Delete the address identified by n. The implementation has room for a finite number of addresses, so if osc_server_reply() is used to get client reply ports and clients reconnect often, the server should try to remove stale reply ports to avoid filling up the address table.

osc_send_reply(port)

Normally, there is no need for a client (sender) to have a reply port; however, if the sender wants to receive messages from the server, and if the client is subject to network address translation (NAT), the server should reply to messages rather than sending to a fixed IP address or port number. The client can specify the local port to which replies will be sent by calling osc_send_reply(), where port is a string number in decimal, such as "7771". If this call is not made, a reply port is chosen arbitrarily. After calling osc_send_reply or osc_send, osc_server_poll() can be called to process reply messages. (Do not call osc_server_init). Returns zero on success, negative number on error. osc_send_reply does nothing and returns

-1 in the Liblo version.

osc_send_start()

Prepare to send a message. This should be followed by appending arguments and then sending to a path. It is an error to call osc_send_start() a second time with no intervening call to osc_send.

osc_add_double(x)

Append a double argument x to the current message (which must have been created by

osc_send_start()). osc_add_float(x)

Append a float argument x to the current message (which must have been created by

osc_send_start()). osc_add_int32(i)

Append a 32-bit integer argument i to the current message.

osc_add_int64(i)

Append a 64-bit integer argument i to the current message.

osc_add_string(s)

Append a string argument s to the current message.

osc_add_timetag(i)

Append a 64-bit integer time tag argument i to the current message.

osc_add_symbol(s)

Append a symbol argument s to the current message.

osc_add_char(c)

Append a character (represented in Serpent by a one-character string) argument c to the current message.

osc_add_midi(cmd, d1, d2)

Append a Midi message (represented in Serpent by 3 integers) argument to the current message.

osc_add_bool(b)

Append a boolean argument b to the current message.

osc_add_nil()

Append a nil argument to the current message.

osc_add_infinitum()

Append an "infinitum" argument to the current message.

osc_send(address, path)

Send the constructed arguments to the address, a value returned by osc_create_address. The message is sent to the path, a string. You must call osc_client_start() and append arguments to send another message. A return value of -1 indicates that the address parameter is invalid.

This API is intentionally small and simple. If users find OSC useful and need additional features, feel free to contact the author about extending this specification. Also, any serious OSC client should probably write a Serpent library to at least implement something like osc_send(path, types, arg1, arg2, ...) to construct and send an OSC message.

# ZeroMQ

ZeroMQ is a message passing library and concurrency framework. When Serpent is linked with ZeroMQ, the following functions are available.

zmq_init()

Initialize the ZeroMQ library and a ZeroMQ context to be used by subsequent ZeroMQ function calls.

zmq_open_reply()

Create a socket for reply messages. To use a reply socket, you first receive a message (which was sent from a request socket) and then send a message. ZeroMQ assumes a strict alternation of receive and send. Null is returned on error, otherwise a socket is returned. You should next connect or bind the socket.

zmq_open_request()

Create a socket for request messages. To use a request socket, you first send a request message (which is delivered to a reply socket), then receive the reply. ZeroMQ assumes a strict alternation of send and receive. Null is returned on error, otherwise a socket is returned. You should next connect or bind the socket.

zmq_open_publish()

Create a socket to publish messages. To use a publish socket, you simply send messages where the initial bytes are the topic (see zmq_set_filter). ZeroMQ assumes the socket is send-only. Null is returned on error, otherwise a socket is returned. You should next connect or bind the socket.

zmq_open_subscribe()

Create a socket to subscribe to messages. To use a subscribe socket, you simply receive. ZeroMQ assumes the socket is receive-only. Null is returned on error, otherwise a socket is returned. You should next connect or bind the socket and set the filter. By default, all messages are filtered so no messages are received.

zmq_open_push()

Create a socket for push messages. To use a push socket, you simply send messages to it. ZeroMQ assumes the socket is strictly send only. Null is returned on error, otherwise a socket is returned. You should next connect or bind the socket.

zmq_open_pull()

Create a socket for pull messages. To use a pull socket, you simply receive the reply. ZeroMQ assumes the socket is receive-only. Null is returned on error, otherwise a socket is returned. You should next connect or bind the socket.

zmq_bind(socket, protocol, host, port)

Select the protocol and bind a socket to an address. ZeroMQ connections allow either the "client" or the "server" to call zmq_bind, but one side must use bind, and the other end must use connect. The protocol choices are the strings "tcp", "ipc", or "inproc" (see ZeroMQ documentation for more information on protocols). The host is a string, and the port is an integer. For "tcp," the host is typically "*." For "ipc" the "host" is really the address, e.g. "/tmp/feeds/0", and port is ignored. For "inproc," "host" is really a name, e.g. "myendpoint" and port is ignored. Returns success (true) or failure (false). For "inproc", the bind must take place before a socket is connected.

zmq_connect(socket, protocol, host, port)

Select the protocol and connect a socket to an address. The protocol choices are "tcp", "ipc", or "inproc" (see ZeroMQ documentation). The host is a string, and the port is an integer. For "tcp", the host may be "localhost". For "ipc" and "inproc", port is ignored. Returns success (true) or failure (false). For "inproc", the connect must take place after bind on the other end.

zmq_subscribe(socket, filter)

Sets the filter on a socket opened with the "subscribe" protocol. Messages are received the prefix of the message matches the filter, a string. A socket can contain multiple filters, including duplicates.

zmq_unsubscribe(socket, filter)

Remove a filter that was added to a socket by zmq_subscribe(). zmq_send(socket, message)

Send a message, a string, to a socket. Generally, this call does not block and messages are

queued for the receiver. In some cases, the receiver need not exist at the time of the send. Caution: sending faster that the receiver receives or before the receiver exists implies that the sender can queue an unbounded number of messages. Returns true if and only if successful.

zmq_recv_noblock(socket)

Receive a message, a string, from a socket. If no messages are ready or an error occurs, nil (false) is returned. Otherwise a string is returned. WARNING: If the message is longer than STRMAXLEN-1 (STRMAXLEN is a C++ compile-time constant, not exported to Serpent, and is currently 255), the message is truncated. A sender should limit messages to 254 characters, and receivers should assume data was lost when messages arrive with length 255.

zmq_recv_block(socket)

Block until a message is available. Returns nil (false) if an error occurs. Otherwise, the message is returned as a string. See the warning above on message truncation.

zmq_close(socket)

Close a socket. Returns nil.

zmq_term()

Close the current context and shut down the ZeroMQ library.

# Aura Extensions

Serpent has an extended syntax to support Aura message passing. This syntax is enabled by setting the AURA flag during compilation. Normally, you would only do this when compiling Serpent as a library for linking with Aura, but you can also compile a stand-along Serpent this way.

An Aura message is used to invoke operations on Aura objects. These are "real" messages is the sense that they are represented as a sequence of bytes and they can be sent to objects in other threads or even to other address spaces. Aura messsages have a method identifier (a string) including a type signature and a set of parameters. The type signature for a given method identifier is the same for all objects. For example, the method identifier "set_hz" has one parameter that is a double. All objects that accept the "set_hz" have the same signature and require one double.

## Aura Send

To send an Aura message, you can use one of the following syntax forms: target <- message(p1, p2, p3)

target <- message(p1, p2, p3) @ when

<- message(p1, p2, p3)

<- message(p1, p2, p3) @ when

While this looks like some kind of procedure call, it is quite different. The target, which is optional, is any expression that evaluates to an Aura ID (represented in Serpent as an integer, and usually obtained by a call to the function aura_create_inst, loaded from auramsgs.srp.)

The message must be an identifier that has been declared as an Aura message. Although parsed as an identifier (unquoted), Serpent uses the string name of this identifier to form the method part of an Aura message. The message is also used to find the type signature for the message by using message (now as a symbol) as a key in the Serpent dictionary aura_type_strings. The lookup must succeed at compile time or an error is reported. The result of the lookup is a string consisting of the letters "i" (Long), "d" (Double), "s" (String), "l" (Logical), and "v" (Vector of floats, obtained from a Serpent array).

The parameters p1 through p3 are a comma-separated list of expressions equal in number to the length of the type string for message. The types of these parameters must be compatible with the letters of the type string, but full checking can only be done at run time.

The Aura Send statement is compiled to a call to aura_zone_send_from_to. Normally this is a built- in function that calls into Aura to construct and send a message. The parameters to aura_zone_send_from_to are:

aura_zone_id -- The Aura ID for the current zone. This is obtained from the global variable

aura_zone_id, which must have a value at run time.

aura -- The Aura ID of the sending object. This is 0 if there is a target expression and the message is actually sent from the current zone using aura_zone_id as the sender. If there is no target, then the message is sent to all objects the sender is connected to. In this case, the sender's Aura ID must be in the variable "aura." Normally, the aura send statement would be in the method of a class that inherits from class Aura, which provides an instance variable named aura.

destination -- The Aura ID for the receiver. If a target expression appears, the destination is the value of that expression. Otherwise, destination is 0 and the message is broadcast to all connected receivers.

method -- The string name of the method to be invoked, obtained from message.

parameters -- An array consisting of the type string for method followed by parameter values, obtained by evaluating the parameter expressions. The array is automatically allocated and constructed.

timestamp -- A timestamp giving the Aura time for the message to be delivered. (Aura messages are held in a queue until their delivery time.) The default value is the value of the variable AURA_NOW which must be defined (normally to 1e-9) at runtime.

Note that the Aura preprocessor should be used to generate correct type strings. Do not add type strings to aura_type_strings manually.

For testing, it is possible to compile Serpent using the AURA compile-time flag. You will have to define things expected by the compiler including aura_zone_send_from_to, but this can be an ordinary Serpent function.

### Example

iecho_aura = aura_create_inst("Iecho", 3) iecho_aura <- set_in(audio_io_aura, 0) iecho_aura <- set_delay(0.3)

This creates an "Iecho" instance, sets the input to the left channel (0) of the system audio input, and sets the delay to 0.3 seconds. The last (third) statement is equivalent to the following:

aura_zone_send_from_to(aura_zone_id, 0, iecho_aura,

"set_delay", ["d", 0.3], AURA_NOW)

# Extending Serpent

Serpent can be extended with functions and data types. The interface between Serpent and external code is generated semi-automatically using the Serpent program interface.srp. Not all C types are supported, and the mapping between Serpent and C types has some restrictions and special cases, so sometimes the developer must create some "glue" functions to translate between Serpent and C. The supported types are as follows:

All interfaces are explicitly indicated by adding comments to C code as follows:

/*SER type function_name [c_name] (type1, type2, type3, ...) PENT*/

Generates an interface to function_name, which refers to the Serpent name for the function. If the C name is different, it is specified between square brackets. (Note that bracket characters actually appear in the comment; they are not meta-syntax characters.) The types are parameter types as shown in the first column of the table of types shown above. In addition, "external" types may be specified as extern typename.

Finally, there are cases where the function should have access to the virtual machine, which is a C++ object of type Machine. Serpent programs cannot access the virtual machine as an object, so it is impossible to explicitly pass the machine as a parameter. However, if the type is specified as Machine, a pointer to the machine of the caller will be passed automatically. Since the parameter is implicit, the generated function in Serpent will have one less parameter than the corresponding C function.

/*SER class Class_name PENT*/

Serpent can be extended with new types using this form of comment.

/*SER variable = value PENT*/

Global variables in Serpent can be initialized to a value using this form of comment. The value must be a string, integer, symbol, or real constant. No expressions are allowed. When in doubt, value is converted to symbol.

## Interfaces to Classes and Structures

The files extclass.h and extclass.cpp give an example of an interface to a class. Note the use of the class Descriptor to describe the external class to the Serpent run-time system. Descriptor is subclassed to build a descriptor for the new type. This is not an automatic operation; you must build your own descriptor subclass.

## Interfaces to Functions

The files extfuncdemo.h and extfuncdemo.cpp provide an example of an interface to ordinary functions written in C or C++.

## Building an Interface

Interfaces based on one or more .h file are generated by loading "interface.srp" and calling the

interf function as shown in the following example:

interf("smid", ["midi.h", "midiserpent.h"])

The first parameter specifies the output file name (without the .cpp extension). This name is also used for some internal names that must be generated. The second parameter is a list of files to process. Each of these files is included in the generated output file using an #include directive, so if you want a file included, list it even if it contains no /*SER ... PENT*/ comments.

In order to find header files not in the current directory, you can provide a search path as follows:

interface_search_path = ["..\\midi\\", ...]

# Sublime and Emacs

The Serpent sources include syntax-aware editing mode support for Sublime and Emacs. See serpent/extras/README.txt, which you can find either in the installed source code (if you download all of it), or get the specific files you need by b hosted on sourceforge.net.