# Serpent by Example


## Roger B. Dannenberg


## Introduction

## Arrays

### Introduction


### The Code

```

> a = []
-> []
> a = [5, 6, "hi", 'symb', 3.4]
-> [5, 6, "hi", 'symb', 3.4]
> a[3]
-> symb
> subseq(a, 3)
-> ['symb', 3.4]
> subseq(a, 1, 3)
-> [6, "hi"]
> a.last()
-> 3.4
> a.insert(1, "new")
-> [5, "new", 6, "hi", 'symb', 3.4]
> a.append("newer")
-> [5, "new", 6, "hi", 'symb', 3.4, "newer"]
> a.unappend()
-> "newer"
> a
-> [5, "new", 6, "hi", 'symb', 3.4]
> a.setlen(3)
-> [5, "new", 6]
> len(a)
-> 3
> a.uninsert(1)
-> [5, 6]
> a.reverse()
-> [6, 5]
> a
-> [6, 5]
> b = a
-> [6, 5]
> a is b
-> t
> a.append(4)
-> [6, 5, 4] a is changed
> b
-> [6, 5, 4] note that b was also changed
> b = a.copy()
-> [6, 5, 4]
> a is b
-> nil now, b is a different array
> a.reverse()
-> [4, 5, 6] changing a does not change b
> b
-> [6, 5, 4]


```

```

> a = []
-> []
> a = [5, 6, "hi", 'symb', 3.4]
-> [5, 6, "hi", 'symb', 3.4]
> a[3]
-> symb
> subseq(a, 3)
-> ['symb', 3.4]
> subseq(a, 1, 3)
-> [6, "hi"]
> a.last()
-> 3.4
> a.insert(1, "new")
-> [5, "new", 6, "hi", 'symb', 3.4]
> a.append("newer")
-> [5, "new", 6, "hi", 'symb', 3.4, "newer"]
> a.unappend()
-> "newer"
> a
-> [5, "new", 6, "hi", 'symb', 3.4]
> a.setlen(3)
-> [5, "new", 6]
> len(a)
-> 3
> a.uninsert(1)
-> [5, 6]
> a.reverse()
-> [6, 5]
> a
-> [6, 5]
> b = a
-> [6, 5]
> a is b
-> t
> a.append(4)
-> [6, 5, 4] a is changed
> b
-> [6, 5, 4] note that b was also changed
> b = a.copy()
-> [6, 5, 4]
> a is b
-> nil now, b is a different array
> a.reverse()
-> [4, 5, 6] changing a does not change b
> b
-> [6, 5, 4]


```

## Dialog Boxes


### Introduction

wxSerpent has some built-in dialog boxes for opening files,
      opening directories, getting numbers and text, and displaying
      messages. This example shows how to select a file and display a
      message. Note that wxs_file_selector returns a path to the file --
      it does not open the file. wxs_message_box returns a return code,
      which is one of WXS_MSG_YES, WXS_MSG_NO, WXS_MSG_CANCEL, or
        WXS_MSG_OK.

### The Code

```

# dialog example

require "strparse.srp"
require "debug.srp"
require "wxserpent.srp"

print "calling wxs_file_selector(\"This is an example call";
print " to wxs_file_selector.\", \".\", \"data\", \"txt\",";
print " \"*\", WXS_FILE_OPEN, WXS_DEFAULT_WINDOW)"
print

file_sel = wxs_file_selector(
            "This is an example call to wxs_file_selector.", 
            ".", "data", "txt", "*", WXS_FILE_OPEN,
            WXS_DEFAULT_WINDOW)

print "wxs_file_selector returned this value:"
print " ", file_sel
print
print "calling wxs_message_box(\"This message box has style";
print " WXS_STYLE_INFORMATION.\", \"This is an example call";
print " to wxs_message_box.\", WXS_STYLE_INFORMATION,";
print " WXS_DEFAULT_WINDOW)"
print
msg_box = wxs_message_box(
           "This message box has style WXS_STYLE_INFORMATION.", 
           "This is an example call to wxs_message_box.", 
           WXS_STYLE_INFORMATION, WXS_DEFAULT_WINDOW)

print "wxs_message_box returned this value:"
print " ", msg_box
display "Return values", WXS_MSG_YES, WXS_MSG_NO,
display WXS_MSG_CANCEL, WXS_MSG_OK


```

```

# dialog example

require "strparse.srp"
require "debug.srp"
require "wxserpent.srp"

print "calling wxs_file_selector(\"This is an example call";
print " to wxs_file_selector.\", \".\", \"data\", \"txt\",";
print " \"*\", WXS_FILE_OPEN, WXS_DEFAULT_WINDOW)"
print

file_sel = wxs_file_selector(
            "This is an example call to wxs_file_selector.", 
            ".", "data", "txt", "*", WXS_FILE_OPEN,
            WXS_DEFAULT_WINDOW)

print "wxs_file_selector returned this value:"
print " ", file_sel
print
print "calling wxs_message_box(\"This message box has style";
print " WXS_STYLE_INFORMATION.\", \"This is an example call";
print " to wxs_message_box.\", WXS_STYLE_INFORMATION,";
print " WXS_DEFAULT_WINDOW)"
print
msg_box = wxs_message_box(
           "This message box has style WXS_STYLE_INFORMATION.", 
           "This is an example call to wxs_message_box.", 
           WXS_STYLE_INFORMATION, WXS_DEFAULT_WINDOW)

print "wxs_message_box returned this value:"
print " ", msg_box
display "Return values", WXS_MSG_YES, WXS_MSG_NO,
display WXS_MSG_CANCEL, WXS_MSG_OK


```

## Dictionaries


### Introduction


### The Code

```

> d = {}
-> {}
> d['address'] = "5000 Forbes Ave."
-> 5000 Forbes Ave.
> d['city'] = "Pittsburgh"
-> Pittsburgh
> d['state'] = "PA"
-> PA
> d['zip'] = "15213"
-> 15213
> print d['address']; "\n"; d['city']; ",", d['state'], d['zip']
5000 Forbes Ave.
Pittsburgh, PA 15213
-> nil
> d.keys()
-> ['address', 'city', 'state', 'zip']
> d['country']
runtime exception handler called
exception is: bad key
frame variables: {}
frame pc: 4
frame method: <immediate command 0>
frame class: nil

bad key, debugger invoked.
Method: <immediate command 0>, PC: 4, Line: 10, File: <stdin>
1> >
debugger reads >
Resume execution...
> > 
> d.get('country', "USA") // provides default for attribute
-> USA
> 

```

```

> d = {}
-> {}
> d['address'] = "5000 Forbes Ave."
-> 5000 Forbes Ave.
> d['city'] = "Pittsburgh"
-> Pittsburgh
> d['state'] = "PA"
-> PA
> d['zip'] = "15213"
-> 15213
> print d['address']; "\n"; d['city']; ",", d['state'], d['zip']
5000 Forbes Ave.
Pittsburgh, PA 15213
-> nil
> d.keys()
-> ['address', 'city', 'state', 'zip']
> d['country']
runtime exception handler called
exception is: bad key
frame variables: {}
frame pc: 4
frame method: <immediate command 0>
frame class: nil

bad key, debugger invoked.
Method: <immediate command 0>, PC: 4, Line: 10, File: <stdin>
1> >
debugger reads >
Resume execution...
> > 
> d.get('country', "USA") // provides default for attribute
-> USA
> 

```

## Strings and Characters


### Introduction


### The Code

```

def chars()    # make characters from numbers    var char_a = ord("a") // ascii code for "a"    var alphabet = ""    for i = 0 to 26        alphabet = alphabet + chr(char_a + i)    print alphabet    # strings can be accessed as arrays    display "string access", "abcd"[2]    # some more string functions (apply to chars too of course)    display "string fns", toupper("abcd"), tolower("NeXT")    # find a substring    display "find", find(alphabet, "qrst"), find(alphabet, "qed")        # make a number from a string    display "convert to number", int("123"), real("123.456")

```

```

def chars()    # make characters from numbers    var char_a = ord("a") // ascii code for "a"    var alphabet = ""    for i = 0 to 26        alphabet = alphabet + chr(char_a + i)    print alphabet    # strings can be accessed as arrays    display "string access", "abcd"[2]    # some more string functions (apply to chars too of course)    display "string fns", toupper("abcd"), tolower("NeXT")    # find a substring    display "find", find(alphabet, "qrst"), find(alphabet, "qed")        # make a number from a string    display "convert to number", int("123"), real("123.456")

```

## Linear Search


### Introduction


### The Code

```

data = ["This", "is", "an", "array", "of", "words", "to", "search."]# linear search with for loop, return index of word in data or -1# def search_with_for(data, word)    for i = 0 to len(data)        if data[i] == word           return i    return -1# for-in loop#def search_with_for_in(data, word)    var i = 0    for w in data        if w == word            return i        i = i + 1     return -1# special form of for eliminates call to len#def search_with_for_at(data, word)    for w at i in data // i is the index of w in data        if w == word           return i    return -1# for simple equality searching, use index:#def search_with_index(data, word)    return data.index(word)# test it#display "test 1", search_with_for(data, "of")display "test 2", search_with_for_in(data, "of")display "test 3", search_with_for_at(data, "of")display "test 4", search_with_index(data, "of")

```

```

data = ["This", "is", "an", "array", "of", "words", "to", "search."]# linear search with for loop, return index of word in data or -1# def search_with_for(data, word)    for i = 0 to len(data)        if data[i] == word           return i    return -1# for-in loop#def search_with_for_in(data, word)    var i = 0    for w in data        if w == word            return i        i = i + 1     return -1# special form of for eliminates call to len#def search_with_for_at(data, word)    for w at i in data // i is the index of w in data        if w == word           return i    return -1# for simple equality searching, use index:#def search_with_index(data, word)    return data.index(word)# test it#display "test 1", search_with_for(data, "of")display "test 2", search_with_for_in(data, "of")display "test 3", search_with_for_at(data, "of")display "test 4", search_with_index(data, "of")

```

## Using Multiple Source
      Files

### Introduction


```

# --- init.srp ---load "debug"     // the ".srp" extension is assumedload "sequencer"

```

```

# --- init.srp ---load "debug"     // the ".srp" extension is assumedload "sequencer"

```

### Dependencies

```

# --- sequencer.srp ---require "strparse"     // the ".srp" extension is assumed... other requires ...... class and function definitions ...

```

```

# --- sequencer.srp ---require "strparse"     // the ".srp" extension is assumed... other requires ...... class and function definitions ...

```

## Classes and Objects

### Introduction

### The Code

```

class Account:    var balance    # init() is called automatically when an Account is created    def init(initial_deposit)        balance = initial_deposit    def deposit(x)        balance = balance + x	# note: you could also write this.balance = ...    def withdraw(x)        if balance >= x            balance = balance - x            return balance        else            return false# test#def account_test()    account = Account(0)    account.deposit(5)    display "account_test", account, account.balance    if not account.withdraw(10)        print "don't have $10"# run it ...> account_test()account_test: account = <obj@0x205a48>, account.balance = 5don't have $10-> nil> 

```

```

class Account:    var balance    # init() is called automatically when an Account is created    def init(initial_deposit)        balance = initial_deposit    def deposit(x)        balance = balance + x	# note: you could also write this.balance = ...    def withdraw(x)        if balance >= x            balance = balance - x            return balance        else            return false# test#def account_test()    account = Account(0)    account.deposit(5)    display "account_test", account, account.balance    if not account.withdraw(10)        print "don't have $10"# run it ...> account_test()account_test: account = <obj@0x205a48>, account.balance = 5don't have $10-> nil> 

```

## Inheritance


### Introduction

### The Code

```

class Account:
    var balance
    def init(initial_deposit)
        balance = initial_deposit
    def deposit(x)
        balance = balance + x
    def withdraw(x)
        if balance >= x
            balance = balance - x
            return balance
        else
            return false

# extend the Account class with a name and show method
class Named_account(Account)
    var name
    def init(a_name, initial_deposit)
	# first call superclass's init
	super.init(initial_deposit)
	name = a_name
    def show()
        print name, "has a balance of $"; balance

# test
#
def account_test()
    account = Account(0)
    account.deposit(5)
    display "account_test", account, account.balance
    if not account.withdraw(10)
        print "don't have $10"

def named_account_test()
    named_account = Named_account("Klaatu", 1000)
    named_account.show()
    named_account.withdraw(300) // inherited method
    named_account.show()

# run it ...
> account_test()
account_test: account = <obj@0x205a48>, account.balance = 5
don't have $10
-> nil> named_account_test()
Klaatu has a balance of $1000
Klaatu has a balance of $700


```

```

class Account:
    var balance
    def init(initial_deposit)
        balance = initial_deposit
    def deposit(x)
        balance = balance + x
    def withdraw(x)
        if balance >= x
            balance = balance - x
            return balance
        else
            return false

# extend the Account class with a name and show method
class Named_account(Account)
    var name
    def init(a_name, initial_deposit)
	# first call superclass's init
	super.init(initial_deposit)
	name = a_name
    def show()
        print name, "has a balance of $"; balance

# test
#
def account_test()
    account = Account(0)
    account.deposit(5)
    display "account_test", account, account.balance
    if not account.withdraw(10)
        print "don't have $10"

def named_account_test()
    named_account = Named_account("Klaatu", 1000)
    named_account.show()
    named_account.withdraw(300) // inherited method
    named_account.show()

# run it ...
> account_test()
account_test: account = <obj@0x205a48>, account.balance = 5
don't have $10
-> nil> named_account_test()
Klaatu has a balance of $1000
Klaatu has a balance of $700


```

## Editing Hints


```

(setq auto-mode-alist (cons
        '("\\.srp$" . serpent-mode) auto-mode-alist))

```

```

(setq interpreter-mode-alist (cons '("serpent" .
        serpent-mode) interpreter-mode-alist))

```

```

(autoload 'serpent-mode "serpent-mode" "Serpent editing
        mode." t)

```

```



```

## Sorting a File


### Introduction


### The Code

```

def string_gtr(s1, s2)
    s1 > s2

def filesort(in_file, out_file)
    var inf = open(in_file, "r")
    if not inf
        return "Could not open " + in_file
    var outf = open(out_file, "w")
    if not outf
        return "Could not open " + out_file
    var content = inf.readlines()
    inf.close()
    content.sort('string_gtr')
    outf.writelines(content)
    outf.close()

# test it
#
filesort("unsorted.txt", "sorted.txt")

# another version that sorts by line length
#
def longer(s1, s2)
    len(s1) > len(s2)

def filesort_by_len(in_file, out_file)
    var inf = open(in_file, "r")
    if not inf
        return "Could not open " + in_file
    var outf = open(out_file, "w")
    if not outf
        return "Could not open " + out_file
    var content = inf.readlines()
    inf.close()
    content.sort('longer')
    outf.writelines(content)
    outf.close()

# test it
#
filesort_by_len("unsorted.txt", "by-length.txt")



```

```

def string_gtr(s1, s2)
    s1 > s2

def filesort(in_file, out_file)
    var inf = open(in_file, "r")
    if not inf
        return "Could not open " + in_file
    var outf = open(out_file, "w")
    if not outf
        return "Could not open " + out_file
    var content = inf.readlines()
    inf.close()
    content.sort('string_gtr')
    outf.writelines(content)
    outf.close()

# test it
#
filesort("unsorted.txt", "sorted.txt")

# another version that sorts by line length
#
def longer(s1, s2)
    len(s1) > len(s2)

def filesort_by_len(in_file, out_file)
    var inf = open(in_file, "r")
    if not inf
        return "Could not open " + in_file
    var outf = open(out_file, "w")
    if not outf
        return "Could not open " + out_file
    var content = inf.readlines()
    inf.close()
    content.sort('longer')
    outf.writelines(content)
    outf.close()

# test it
#
filesort_by_len("unsorted.txt", "by-length.txt")



```

## Optional Parameters


### Introduction


### The Code

```

# optargs.srp -- optional parameter examples
#
# Roger B. Dannenberg
# Jan, 2010

#---- example of "rest" parameter ----
#
# form sum of all arguments
#
def sum(rest a)
    var s = 0
    for x in a
        s = s + x
    s // just "s", or you can say "return s"


# test it
#
display "call sum", sum(1, 2, 3, 4, 5)


#---- example of optional parameter ----
#
# convert to string and print with arbitrary "quote" strings
#
def print_quoted(s, optional quote = "\"")
    print quote + str(s) + quote


# test it
#
def print_quoted_tests()
    print "test: print_quoted(23) prints ... ";
    print_quoted(23)
    print "test: print_quoted(23, \"'\") prints ... ";
    print_quoted(23, "'")
    print "test: print_quoted(23, \"\") prints ... ";
    print_quoted(23, "")
    print "test: print_quoted(\"hello world\", \"|\") prints ... ";
    print_quoted("hello world", "|")

    
print_quoted_tests()


#---- example of keyword parameter ----
#
# print the time
#
def print_within(s, keyword prefix = "", keyword suffix = "")
    print prefix; str(s); suffix


# test it
#
def print_within_tests()
    print "test: print_within(23) prints ... ";
    print_within(23)
    print "test: print_within(\"My Paragraph\", prefix = \"<p>\") prints ... ";
    print_within("My Paragraph", prefix = "<p>")
    print "test: print_within(\"My Heading\", "
    print "          prefix = \"<h1>\", suffix = \"</h1>\") prints ... ";
    print_within(23, prefix = "<h1>", suffix = "</h1>")


print_within_tests()


#---- example of dictionary parameter ----
#
# print keywords and their values
#
def print_args(required_parameter, dictionary d)
    var keys = d.keys()
    print "required_parameter =", required_parameter
    for k in keys
        print k, "=", d[k]

# test it
#
def print_args_test()
    print "calling print_args(a = 1, b = 2, c = 3) ..."
    print_args(123, a = 1, b = 2, c = 3)
    print "... done"

print_args_test()


```

```

# optargs.srp -- optional parameter examples
#
# Roger B. Dannenberg
# Jan, 2010

#---- example of "rest" parameter ----
#
# form sum of all arguments
#
def sum(rest a)
    var s = 0
    for x in a
        s = s + x
    s // just "s", or you can say "return s"


# test it
#
display "call sum", sum(1, 2, 3, 4, 5)


#---- example of optional parameter ----
#
# convert to string and print with arbitrary "quote" strings
#
def print_quoted(s, optional quote = "\"")
    print quote + str(s) + quote


# test it
#
def print_quoted_tests()
    print "test: print_quoted(23) prints ... ";
    print_quoted(23)
    print "test: print_quoted(23, \"'\") prints ... ";
    print_quoted(23, "'")
    print "test: print_quoted(23, \"\") prints ... ";
    print_quoted(23, "")
    print "test: print_quoted(\"hello world\", \"|\") prints ... ";
    print_quoted("hello world", "|")

    
print_quoted_tests()


#---- example of keyword parameter ----
#
# print the time
#
def print_within(s, keyword prefix = "", keyword suffix = "")
    print prefix; str(s); suffix


# test it
#
def print_within_tests()
    print "test: print_within(23) prints ... ";
    print_within(23)
    print "test: print_within(\"My Paragraph\", prefix = \"<p>\") prints ... ";
    print_within("My Paragraph", prefix = "<p>")
    print "test: print_within(\"My Heading\", "
    print "          prefix = \"<h1>\", suffix = \"</h1>\") prints ... ";
    print_within(23, prefix = "<h1>", suffix = "</h1>")


print_within_tests()


#---- example of dictionary parameter ----
#
# print keywords and their values
#
def print_args(required_parameter, dictionary d)
    var keys = d.keys()
    print "required_parameter =", required_parameter
    for k in keys
        print k, "=", d[k]

# test it
#
def print_args_test()
    print "calling print_args(a = 1, b = 2, c = 3) ..."
    print_args(123, a = 1, b = 2, c = 3)
    print "... done"

print_args_test()


```

## Parsing Text 

### Introduction


### The Code

```

// String_parser is not built-in, so you must load the// code if it has not already been loaded...require "strparse"# return an array of fields from an input string#def fields(s)    var sp = String_parse(s) // create and initialize the                              // String_parser object    var result = [] // create empty array to accumulate results    sp.skip_space() // this is not necessary -- just illustrating    var field = sp.get_nonspace() // parse out a field    while field != "" // get all the fields        result.append(field) // append each field to array        field = sp.get_nonspace()    return result# test it#print "fields(\"This is a test 123 %$&!\") returns",print fields("This is a test 123 %$&!")

```

```

// String_parser is not built-in, so you must load the// code if it has not already been loaded...require "strparse"# return an array of fields from an input string#def fields(s)    var sp = String_parse(s) // create and initialize the                              // String_parser object    var result = [] // create empty array to accumulate results    sp.skip_space() // this is not necessary -- just illustrating    var field = sp.get_nonspace() // parse out a field    while field != "" // get all the fields        result.append(field) // append each field to array        field = sp.get_nonspace()    return result# test it#print "fields(\"This is a test 123 %$&!\") returns",print fields("This is a test 123 %$&!")

```

## Applying Functions


### Introduction


### The Code

```

> def adder(x, y) // define a simple function 
>     x + y
> apply('adder', [5, 7]) // function is a Symbol, args are in an array
-> 12
> funcall('adder', 5, 7) // function is a Symbol, args in ordinary list
-> 12
> fn = 'adder'    // you can of course use variables so that functions
-> 'adder'
> args = [4, 9]   // and arguments depend on computation...
-> [4, 9]
> apply(fn, args)
-> 13
> require "strparse" // load a class
> s = String_parse("test string")
> meth = 'get_nonspace'
> send(s, meth)
-> test
> sendapply(s, meth, []) // pass an empty array if there are no arguments
-> string


```

```

> def adder(x, y) // define a simple function 
>     x + y
> apply('adder', [5, 7]) // function is a Symbol, args are in an array
-> 12
> funcall('adder', 5, 7) // function is a Symbol, args in ordinary list
-> 12
> fn = 'adder'    // you can of course use variables so that functions
-> 'adder'
> args = [4, 9]   // and arguments depend on computation...
-> [4, 9]
> apply(fn, args)
-> 13
> require "strparse" // load a class
> s = String_parse("test string")
> meth = 'get_nonspace'
> send(s, meth)
-> test
> sendapply(s, meth, []) // pass an empty array if there are no arguments
-> string


```

## String Processing:
      Flatten

### Introduction


### The Code

```

# the fast way to build a big stringdef flatten_example()    var text = []    for i = 0 to 1000        text.append(str(i)) // appending to arrays is efficient        text.append(",")    // now "flatten" the strings in the array to one string    return flatten(text)# test it#print flatten_example()# nested arrays can be flattened tooprint flatten(["a", "b", ["c", "d"], "e"])

```

```

# the fast way to build a big stringdef flatten_example()    var text = []    for i = 0 to 1000        text.append(str(i)) // appending to arrays is efficient        text.append(",")    // now "flatten" the strings in the array to one string    return flatten(text)# test it#print flatten_example()# nested arrays can be flattened tooprint flatten(["a", "b", ["c", "d"], "e"])

```

## Random Numbers and Choices

### Introduction

```

lib/prob.srp

```

- pr_choice(list, [source]) - pick an element from
        an array at random. If source (optional) is
        provided, choose without replacement: The chosen element is
        removed from list, and before choosing, if list
        is empty, list is replenished by inserting all
        elements of source. (In practice, it is expected
        that each time you call pr_choice(), you pass in
        the same source list.)

- pr_gaussian() - return a random number from a
        Gaussian distribution, with mean 0 and standard deviation 1.

- pr_markov(state, table) -
          pick a next state given a current state in a Markov chain. state
          is the current state, expressed as an integer index. table
          is a table (array) of transition probabilities. Each element
          of table is an array of transition
          probabilities. Thus, the table is considered a
          two-dimensional array, or an array of rows, where each row
          gives transition probabilities for a different current state.

- pr_normal(mu, sigma, low, high) - draw from a
        normal (Guassian) distribution with mean mu,
        standard deviation sigma, with optional low and
        high limit values. This is an iterative algorithm that
        repeatedly computes a random value until the value falls within
        the low and high limits.

- pr_range([low], high) - pick an integer that is
        greater than or equal to low and less than high.
        The default for low is zero.

- pr_unif([low], high) - pick a real number that is
        greater than or equal to low (default is zero) and less than
        high, with uniform distribution.

- pr_weighted_choice(weights) - Pick an index
        according to weights. weights is an array of
        weights. E.g. pr_weigthed_choice([1, 2]) will
        return 0 with probability 1/3 and 1 with probability 2/3.

```

pr_choice(list, [source])

```

```

source

```

```

list

```

```

list

```

```

list

```

```

source

```

```

pr_choice()

```

```

source

```

```

pr_gaussian()

```

```

pr_markov(state, table)

```

```

state

```

```

table

```

```

table

```

```

table

```

```

pr_normal(mu, sigma, low, high)

```

```

mu

```

```

sigma

```

```

pr_range([low], high)

```

```

low

```

```

high

```

```

low

```

```

pr_unif([low], high)

```

```

pr_weighted_choice(weights)

```

```

weights

```

```

pr_weigthed_choice([1, 2])

```

## Repr vs Str

### Introduction


### The Code

```

def str_repr()    display "str", str("abc"), len(str("abc"))    display "repr", repr("abc"), len(repr("abc"))    // the backslash is used to insert special characters in a string    // \n is newline, \t is tab, \\ is one backslash, \r is return    // \" is a double quote, \' is a single quote    var tricky = "quoted: \"abc\"" // the string is: quoted: "abc"    display "embedded quotes problem", repr(tricky)    // repr(tricky) does not escape the quotes, so the result is not    //     machine readable    // print a quoted string with escaped quotes:    display "a solution", string_escape("quoted:\"abc\"", "\"")    // how to print a symbol with embedded escaped quotes:    display "symbol", string_escape(str('it\'s'), "'")

```

```

def str_repr()    display "str", str("abc"), len(str("abc"))    display "repr", repr("abc"), len(repr("abc"))    // the backslash is used to insert special characters in a string    // \n is newline, \t is tab, \\ is one backslash, \r is return    // \" is a double quote, \' is a single quote    var tricky = "quoted: \"abc\"" // the string is: quoted: "abc"    display "embedded quotes problem", repr(tricky)    // repr(tricky) does not escape the quotes, so the result is not    //     machine readable    // print a quoted string with escaped quotes:    display "a solution", string_escape("quoted:\"abc\"", "\"")    // how to print a symbol with embedded escaped quotes:    display "symbol", string_escape(str('it\'s'), "'")

```

```

> load "str-repr"
str: str("abc") = abc, len(str("abc")) = 3
repr: repr("abc") = "abc", len(repr("abc")) = 5
embedded quotes problem: repr(tricky) = "quoted: "abc""
a solution: string_escape("quoted:\"abc\"", "\"") = "quoted:\"abc\""
symbol: string_escape(str('it\'s'), "'") = 'it\'s'
-> nil

```

```

> load "str-repr"
str: str("abc") = abc, len(str("abc")) = 3
repr: repr("abc") = "abc", len(repr("abc")) = 5
embedded quotes problem: repr(tricky) = "quoted: "abc""
a solution: string_escape("quoted:\"abc\"", "\"") = "quoted:\"abc\""
symbol: string_escape(str('it\'s'), "'") = 'it\'s'
-> nil

```

## Midi

### Introduction

This section illustrates direct MIDI I/O using Serpent
      primitives. A higher-level interface that integrates MIDI and
      scheduling is described in Introduction
        to Scheduling.


 This example also shows how timestamps can be used with MIDI. WARNING:
      Queueing up many messages is generally a bad idea. At the very
      least, queueing messages removes any ability to change parameters,
      stop quickly, or insert notes on a new channel (messages are
      delivered in order of writes and are not sorted into time order).

 Notice in this example that we delay until the desired output
      time before writing. However, since the latency parameter is 10
      (ms) (in midi_open_output()), the message will be
      delayed an additional 10ms relative to the timestamp, which gives
      the device driver the opportunity to correct any timing errors in
      case time_sleep() wakes up a few milliseconds late.
    

```

midi_open_output()

```

```

time_sleep()

```

See also serpent/programs/midi_out_test.srp, which
      does not use timestamps, but illustrates
      midi_get_device_info(). A nicer
      show_midi_devices() function can be found in
      serpent/programs/midi-io.srp. 
    

```

serpent/programs/midi_out_test.srp

```

```

midi_get_device_info()

```

```

show_midi_devices()

```

```

serpent/programs/midi-io.srp

```

Finally, these are all low-level examples. For serious work, you
      probably want to use a scheduler (serpent/lib/sched.srp),
      the midi-io functions (serpent/programs/midi-io.srp),
      and if you use wxSerpent, you can get menu-based device selection
      using serpent/programs/mididevice.srp, which has an
      example in serpent/programs/mididevice-demo.srp. 

```

serpent/lib/sched.srp

```

```

serpent/programs/midi-io.srp

```

```

serpent/programs/mididevice.srp

```

```

serpent/programs/mididevice-demo.srp

```

### The Code

```

def midi_example()
    var midi_out = midi_create() // create an unopened PortMidi stream
    var midi_dev = midi_out_default() // find default device number
    // Note: you can query and select available devices, but much
    // simpler to open the default device. Choose the default with the
    // PmDefault application in PortMidi
    if midi_open_output(midi_out, midi_dev, 100, 10) != 0
        print "Error opening default MIDI device for output"
        return
    display "sending first MIDI message", time_get()
    // play a note
    var now = int(time_get() * 1000) // integer milliseconds
    for i = 0 to 20
        now = now + 100
        time_sleep(now / 1000 - time_get()) // wait until now
        var note_on = 0x90 + ((60 + i) << 8) + (100 << 16)
        midi_write(midi_out, now, note_on)
        now = now + 100
        time_sleep(now / 1000 - time_get()) // wait until now
        var note_off = 0x90 + ((60 + i) << 8) // + (0 << 16)
        midi_write(midi_out, now, note_off) 
    display "last MIDI message sent", time_get()
    time_sleep(1.0) // make sure all notes play before closing
    midi_close(midi_out)


# test it
#
midi_example()


```

```

def midi_example()
    var midi_out = midi_create() // create an unopened PortMidi stream
    var midi_dev = midi_out_default() // find default device number
    // Note: you can query and select available devices, but much
    // simpler to open the default device. Choose the default with the
    // PmDefault application in PortMidi
    if midi_open_output(midi_out, midi_dev, 100, 10) != 0
        print "Error opening default MIDI device for output"
        return
    display "sending first MIDI message", time_get()
    // play a note
    var now = int(time_get() * 1000) // integer milliseconds
    for i = 0 to 20
        now = now + 100
        time_sleep(now / 1000 - time_get()) // wait until now
        var note_on = 0x90 + ((60 + i) << 8) + (100 << 16)
        midi_write(midi_out, now, note_on)
        now = now + 100
        time_sleep(now / 1000 - time_get()) // wait until now
        var note_off = 0x90 + ((60 + i) << 8) // + (0 << 16)
        midi_write(midi_out, now, note_off) 
    display "last MIDI message sent", time_get()
    time_sleep(1.0) // make sure all notes play before closing
    midi_close(midi_out)


# test it
#
midi_example()


```

## Standard MIDI Files

### Introduction

Serpent has a built-in primitive for reading and parsing Standard
      Midi Files, but using it directly is difficult that we do not even
      document it, except for mentioning it here. The primitives allow
      you to create an object with smfr_create() and read
      a file with smfr_initialize(). The built-in code
      parses a file and calls methods in a provided object, so you have
      to decide what to do with each event in the Standard MIDI File.
    

```

smfr_create()

```

```

smfr_initialize()

```

A class, Midifile_reader is provided in programs/mfread.srp
      to provide event handler methods to smfr_initialize().
      It uses another class to store MIDI file data in a fairly general
      data structure for music data that we describe next.
    

```

Midifile_reader

```

```

programs/mfread.srp

```

```

smfr_initialize()

```

Finally, the data ends up in an instance of Alg_seq
      which is implemented in programs/allegro.srp. This
      data structure, called Allegro, is a general representation for
      music data that can express MIDI and much more. All musical events
      have an extensible property list with arbitrary attributes and
      values. Allegro comes with a number of editing operations, and it
      can be written as Standard MIDI Files or a text format called
      Allegro. You can also play Alg_seq sequences using
      MIDI. There is a C version of the Allegro library that forms the
      bases for Note Tracks in Audacity, and Audacity can read the
      Allegro format files.
    

```

Alg_seq

```

```

programs/allegro.srp

```

```

Alg_seq

```

### How It Works

```

wxs_file_selector()

```

```

allegro_smf_read()

```

```

programs/mfread.srp

```

```

Midifile_reader

```

```

Alg_seq

```

Events in an Alg_seq contain timestamps, which can
      be either seconds or beats. The call seq.convert_to_beats()
      makes all of the timestamps be beats. You can also write seq.convert_to_seconds()
      to get seconds. (Allegro sequences (Alg_seqs) store
      a representation of all tempo changes, which is used to convert
      back and forth from seconds to beats.)
    

```

Alg_seq

```

```

seq.convert_to_beats()

```

```

seq.convert_to_seconds()

```

```

Alg_seq

```

Next, the code uses a nested loop: for each track, for each note
      in the track, print some fields from the note.
    

### The Code

```

require "debug"
require "allegro"
require "mfread"

def warning(msg)
    print "*** "; msg

midi_file_path = wxs_file_selector("Open a Standard MIDI File", 
                         "", "", ".mid", "*.mid", WXS_FILE_OPEN, 0)
print "Opening", midi_file_path
seq = allegro_smf_read(midi_file_path)
if not seq
    print "Could not read", midi_file_path
    exit()

# convert seq times to beats
seq.convert_to_beats()
# to get seconds: seq.convert_to_seconds()

# print the notes in seq
def show_note(note)
    print "time: "; note.time; " chan: "; note.chan; 
    print " keyno: "; note.key; " vel: "; note.loud

for track at tr in seq.tracks
    print "TRACK", tr
    for note in track
        if isinstance(note, Alg_note)
            show_note(note)
exit()


```

```

require "debug"
require "allegro"
require "mfread"

def warning(msg)
    print "*** "; msg

midi_file_path = wxs_file_selector("Open a Standard MIDI File", 
                         "", "", ".mid", "*.mid", WXS_FILE_OPEN, 0)
print "Opening", midi_file_path
seq = allegro_smf_read(midi_file_path)
if not seq
    print "Could not read", midi_file_path
    exit()

# convert seq times to beats
seq.convert_to_beats()
# to get seconds: seq.convert_to_seconds()

# print the notes in seq
def show_note(note)
    print "time: "; note.time; " chan: "; note.chan; 
    print " keyno: "; note.key; " vel: "; note.loud

for track at tr in seq.tracks
    print "TRACK", tr
    for note in track
        if isinstance(note, Alg_note)
            show_note(note)
exit()


```

## Graphical Interfaces Overview


##  Creating a Button


### Introduction

### The Code

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_button.
// Parameters are parent, label, x, y, width, height:
my_button = Button(WXS_DEFAULT_WINDOW, "Click Me", 25, 5, 70, 25)

// Tell button who to call when pressed:
my_button.method = 'my_button_handler' // function to call

// Every handler takes 4 parameters:
def my_button_handler(obj, event, x, y)
    // but for buttons, parameters are not so useful
    print "my_button was clicked. As if you didn't know."



```

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_button.
// Parameters are parent, label, x, y, width, height:
my_button = Button(WXS_DEFAULT_WINDOW, "Click Me", 25, 5, 70, 25)

// Tell button who to call when pressed:
my_button.method = 'my_button_handler' // function to call

// Every handler takes 4 parameters:
def my_button_handler(obj, event, x, y)
    // but for buttons, parameters are not so useful
    print "my_button was clicked. As if you didn't know."



```

### The Code

```

require "wxserpent"

// declare a simple class and instantiate an object
class Counter
    var count
    def init()
        count = 0
    def increment(rest ignore) // ignore all parameters
        count = count + 1
        display "Counter", count

counter = Counter() // create an instance

// make a button to call the increment method
// notice that increment method must accept the 4 parameters
// passed to all graphical control handlers
obj_button = Button(WXS_DEFAULT_WINDOW, "Invoke a Method", 25, 75, 150, 25)
obj_button.target = counter
obj_button.method = 'increment'



```

```

require "wxserpent"

// declare a simple class and instantiate an object
class Counter
    var count
    def init()
        count = 0
    def increment(rest ignore) // ignore all parameters
        count = count + 1
        display "Counter", count

counter = Counter() // create an instance

// make a button to call the increment method
// notice that increment method must accept the 4 parameters
// passed to all graphical control handlers
obj_button = Button(WXS_DEFAULT_WINDOW, "Invoke a Method", 25, 75, 150, 25)
obj_button.target = counter
obj_button.method = 'increment'



```

## Creating a Slider

### Introduction

### The Code

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_slider, but you
// could open another window and put the slider there instead.
// Parameters are parent, minimum value (an integer), maximum value
// (an integer), initial value (an integer), x, y, width, height
// (all coordinates and sizes are integers):
my_slider = Slider(WXS_DEFAULT_WINDOW, 0, 127, 0, 5, 150, 100, 20)
my_slider.method = 'my_slider_handler' // function to call

def my_slider_handler(obj, event, x, y)
    print "my_slider hit", event, "value:", x
    my_gauge.set_value(x) // forward reference to object created next...

// A Gauge is an "analog" value indicator something like one bar of a
// bar graph. The parameters are parent window, range (an integer), and
// x, y, width, height bounding box coordinates (all integers):
my_gauge = Gauge(WXS_DEFAULT_WINDOW, 127, 5, 175, 100, 10)

```

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_slider, but you
// could open another window and put the slider there instead.
// Parameters are parent, minimum value (an integer), maximum value
// (an integer), initial value (an integer), x, y, width, height
// (all coordinates and sizes are integers):
my_slider = Slider(WXS_DEFAULT_WINDOW, 0, 127, 0, 5, 150, 100, 20)
my_slider.method = 'my_slider_handler' // function to call

def my_slider_handler(obj, event, x, y)
    print "my_slider hit", event, "value:", x
    my_gauge.set_value(x) // forward reference to object created next...

// A Gauge is an "analog" value indicator something like one bar of a
// bar graph. The parameters are parent window, range (an integer), and
// x, y, width, height bounding box coordinates (all integers):
my_gauge = Gauge(WXS_DEFAULT_WINDOW, 127, 5, 175, 100, 10)

```

 Similarly, my_gauge
      is used in my_slider_handler()
      before it is given a value in the last line. That is valid because
      Serpent does not check that the variable my_gauge referenced in my_slider_handler() has a
      value until the function is called. By then, my_gauge will have a
      value. 

## Creating a Listbox

### Introduction

### The Code

```

require "debug"
require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_button.
Statictext(WXS_DEFAULT_WINDOW, "Single selection Listbox", 5, 5, 100, 20)
listbox = Listbox(WXS_DEFAULT_WINDOW, 5, 25, 100, 50, false)

def load_strings(lb):
    # strings in listbox'es are added using append():
    lb.append("cello")
    lb.append("flute")
    lb.append("trumpet")
    lb.append("violin")

load_strings(listbox)
listbox.method = 'listbox_handler' // function to call for user actions

print "There are", listbox.get_count(), "items in the Listbox:"
for i = 0 to listbox.get_count():
    print "    ", listbox.get_string(i)


def listbox_handler(obj, event, x, y)
    # handle listbox interaction events.
    # Every handler takes 4 parameters:
    #   obj - the listbox
    #   event - the interaction event type
    #           event is WXS_LISTBOX_SELECTED
    #           when there is a new selection
    #   x, y - depend on the event
    display "listbox event", obj, event, x, y, obj.get_count()
    display "handler", obj.get_selections(), obj.value()
    


// Listbox'es can allow multiple selections. Here is another listbox
// to illustrate this feature and how to use it
Statictext(WXS_DEFAULT_WINDOW, "Multiple selection Listbox", 5, 125, 100, 20)
listbox_m = Listbox(WXS_DEFAULT_WINDOW, 5, 150, 100, 50, true)
load_strings(listbox_m) // put the same strings in it
listbox_m.method = 'listbox_handler' // function to call for user actions

print "There are", listbox_m.get_count(), "items in the Listbox:"
for i = 0 to listbox_m.get_count():
    print "    ", listbox_m.get_string(i)

    

// Listbox'es can allow multiple selections. Here is another listbox
// to illustrate this feature and how to use it
Statictext(WXS_DEFAULT_WINDOW, "Multiple selection Listbox", 5, 125, 100, 20)
listbox_m = Listbox(WXS_DEFAULT_WINDOW, 5, 150, 100, 50, true)
load_strings(listbox_m) // put the same strings in it
listbox_m.method = 'listbox_handler' // function to call for user actions


```

```

require "debug"
require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_button.
Statictext(WXS_DEFAULT_WINDOW, "Single selection Listbox", 5, 5, 100, 20)
listbox = Listbox(WXS_DEFAULT_WINDOW, 5, 25, 100, 50, false)

def load_strings(lb):
    # strings in listbox'es are added using append():
    lb.append("cello")
    lb.append("flute")
    lb.append("trumpet")
    lb.append("violin")

load_strings(listbox)
listbox.method = 'listbox_handler' // function to call for user actions

print "There are", listbox.get_count(), "items in the Listbox:"
for i = 0 to listbox.get_count():
    print "    ", listbox.get_string(i)


def listbox_handler(obj, event, x, y)
    # handle listbox interaction events.
    # Every handler takes 4 parameters:
    #   obj - the listbox
    #   event - the interaction event type
    #           event is WXS_LISTBOX_SELECTED
    #           when there is a new selection
    #   x, y - depend on the event
    display "listbox event", obj, event, x, y, obj.get_count()
    display "handler", obj.get_selections(), obj.value()
    


// Listbox'es can allow multiple selections. Here is another listbox
// to illustrate this feature and how to use it
Statictext(WXS_DEFAULT_WINDOW, "Multiple selection Listbox", 5, 125, 100, 20)
listbox_m = Listbox(WXS_DEFAULT_WINDOW, 5, 150, 100, 50, true)
load_strings(listbox_m) // put the same strings in it
listbox_m.method = 'listbox_handler' // function to call for user actions

print "There are", listbox_m.get_count(), "items in the Listbox:"
for i = 0 to listbox_m.get_count():
    print "    ", listbox_m.get_string(i)

    

// Listbox'es can allow multiple selections. Here is another listbox
// to illustrate this feature and how to use it
Statictext(WXS_DEFAULT_WINDOW, "Multiple selection Listbox", 5, 125, 100, 20)
listbox_m = Listbox(WXS_DEFAULT_WINDOW, 5, 150, 100, 50, true)
load_strings(listbox_m) // put the same strings in it
listbox_m.method = 'listbox_handler' // function to call for user actions


```

 In the last line of the handler, we print obj.get_selections(),
      which returns an array of everything selected. This will be an
      array of (at most) one element in the case of the first listbox,
      which does not allow multiple selections. In that case, notice
      that both the formal parameter x and the method value() provide
      the single selection. 



## Creating Menus

### Introduction

### The Code

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It is the parent of my_menu, but you
// could open another window and put the menu there instead.

Statictext(WXS_DEFAULT_WINDOW, "Please try the Command menu",
           10, 10, 300, 30)

// Create a Menu; parameters are parent and menu name.
my_menu = Menu(WXS_DEFAULT_WINDOW, "Command")
my_menu.method = 'my_menu_handler' // function to call

// Add items to a menu using the item method. Parameters
// are name (string), help string, and checkable (boolean)
my_menu.item("Hello World", "print Hello World", false)

// The separator() method inserts a separator into the menu
my_menu.separator()

// If checkable is true, the menu item has a boolean state
// and will display a check mark when the state is true
my_menu.item("Trace", "print some trace info", true)
// this flag will be controlled by the Trace menu item
menu_trace_flag = false

def my_menu_handler(obj, event, x, y)
    if menu_trace_flag
        display "my_menu_handler", obj, event, x, y
    if event != WXS_MENU_SELECTED
        return // ignore anything other than menu item selection
    if x == 0 // first menu item
        print "Hello World"
    elif x == 1 // the separator
        print "This never prints because you cannot select a separator"
    elif x == 2 // second menu item
        // y == 0 => not checked; y == 1 => checked
        menu_trace_flag = (y == 1)
        print "trace"
    

```

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It is the parent of my_menu, but you
// could open another window and put the menu there instead.

Statictext(WXS_DEFAULT_WINDOW, "Please try the Command menu",
           10, 10, 300, 30)

// Create a Menu; parameters are parent and menu name.
my_menu = Menu(WXS_DEFAULT_WINDOW, "Command")
my_menu.method = 'my_menu_handler' // function to call

// Add items to a menu using the item method. Parameters
// are name (string), help string, and checkable (boolean)
my_menu.item("Hello World", "print Hello World", false)

// The separator() method inserts a separator into the menu
my_menu.separator()

// If checkable is true, the menu item has a boolean state
// and will display a check mark when the state is true
my_menu.item("Trace", "print some trace info", true)
// this flag will be controlled by the Trace menu item
menu_trace_flag = false

def my_menu_handler(obj, event, x, y)
    if menu_trace_flag
        display "my_menu_handler", obj, event, x, y
    if event != WXS_MENU_SELECTED
        return // ignore anything other than menu item selection
    if x == 0 // first menu item
        print "Hello World"
    elif x == 1 // the separator
        print "This never prints because you cannot select a separator"
    elif x == 2 // second menu item
        // y == 0 => not checked; y == 1 => checked
        menu_trace_flag = (y == 1)
        print "trace"
    

```

## Creating Static Text

## Creating a Text Input Box

### Introduction

### The Code

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_textctrl.
// Parameters are parent, initial text, x, y, width, height:
my_textctrl = Textctrl(WXS_DEFAULT_WINDOW, "Hello World", 25, 5, 200, 25)

// Tell Textctrl who to call when pressed:
my_textctrl.method = 'my_textctrl_handler' // function to call

// Every handler takes 4 parameters:
def my_textctrl_handler(obj, event, x, y)
    // for Textctrl, parameters are not so useful, but get_value()
    // can be used to get the text in the box. Not the use of "\""
    // which is a string containing a quote character ("\" is the
    // "escape" character that quotes the next character):
    print "my_textctrl has \""; my_textctrl.value(); "\""


```

```

require "wxserpent"

// WXS_DEFAULT_WINDOW is the initial window created automatically
// when you run wxserpent. It's the parent of my_textctrl.
// Parameters are parent, initial text, x, y, width, height:
my_textctrl = Textctrl(WXS_DEFAULT_WINDOW, "Hello World", 25, 5, 200, 25)

// Tell Textctrl who to call when pressed:
my_textctrl.method = 'my_textctrl_handler' // function to call

// Every handler takes 4 parameters:
def my_textctrl_handler(obj, event, x, y)
    // for Textctrl, parameters are not so useful, but get_value()
    // can be used to get the text in the box. Not the use of "\""
    // which is a string containing a quote character ("\" is the
    // "escape" character that quotes the next character):
    print "my_textctrl has \""; my_textctrl.value(); "\""


```

## 
Creating a New Window

## 
Creating a Panel
          (Subwindow)

## 
Drawing on a Canvas

## 
Creating a Scrolling
          Panel

## 
Creating a Scrolling
          Canvas

### Introduction

### The Code

```

require "debug"
require "wxserpent"

MY_CANVAS_WIDTH = 500
MY_CANVAS_HEIGHT = 2000

// create a subclass of Scrolled_canvas
class My_canvas (Scrolled_canvas)
    def init(parent, x, y, w, h)
        super.init(parent, x, y, w, h)
        set_virtualsize(MY_CANVAS_WIDTH, MY_CANVAS_HEIGHT)

    def paint(flag):
        for x = 50 to MY_CANVAS_WIDTH by 150:
            for y = 50 to MY_CANVAS_HEIGHT by 100:
                set_brush_color("YELLOW") // so text is visible
                draw_rectangle(x, y, 100, 20)
                draw_text(x + 3, y + 3, "(" + str(x) + ", " + str(y) + ")")

    // implement the action of the button. Catch all parameters in "rest" so
    // you can call do_jump() with no parameters, OR call it as an event
    // handler that gets obj, event, x, and y parameters...
    def do_jump(rest ignore):
        scroll(int(MY_CANVAS_WIDTH / 2), int(MY_CANVAS_HEIGHT / 2))

my_canvas = My_canvas(WXS_DEFAULT_WINDOW, 0, 0, 200, 200)

// make a button that jumps to a middle location
jump = Button(WXS_DEFAULT_WINDOW, "Jump", 220, 20, 100, 30)
jump.method = 'do_jump'
jump.target = my_canvas



```

```

require "debug"
require "wxserpent"

MY_CANVAS_WIDTH = 500
MY_CANVAS_HEIGHT = 2000

// create a subclass of Scrolled_canvas
class My_canvas (Scrolled_canvas)
    def init(parent, x, y, w, h)
        super.init(parent, x, y, w, h)
        set_virtualsize(MY_CANVAS_WIDTH, MY_CANVAS_HEIGHT)

    def paint(flag):
        for x = 50 to MY_CANVAS_WIDTH by 150:
            for y = 50 to MY_CANVAS_HEIGHT by 100:
                set_brush_color("YELLOW") // so text is visible
                draw_rectangle(x, y, 100, 20)
                draw_text(x + 3, y + 3, "(" + str(x) + ", " + str(y) + ")")

    // implement the action of the button. Catch all parameters in "rest" so
    // you can call do_jump() with no parameters, OR call it as an event
    // handler that gets obj, event, x, and y parameters...
    def do_jump(rest ignore):
        scroll(int(MY_CANVAS_WIDTH / 2), int(MY_CANVAS_HEIGHT / 2))

my_canvas = My_canvas(WXS_DEFAULT_WINDOW, 0, 0, 200, 200)

// make a button that jumps to a middle location
jump = Button(WXS_DEFAULT_WINDOW, "Jump", 220, 20, 100, 30)
jump.method = 'do_jump'
jump.target = my_canvas



```

## Interactive Drawing

### Introduction

### The Code

```

require "debug"
require "wxserpent"

// create a subclass of Canvas -- you need to subclass Canvas in
// order to override the paint() method, which is how you make
// custom graphics
//
class Drawing (Canvas)
    // the state is an array of lines, where each line is an array
    // of x1, y1, x2, y2 coordinates for the endpoints of lines
    var lines
    var mouse_is_down

    // override init() in order to intialize the state of this
    // subclass, but pass the usuall parent, x, y, w, h parameters
    // to the init() method defined in the Canvas class so that
    // the Canvas state is also initialized.
    //
    def init(parent, x, y, w, h)
        super.init(parent, x, y, w, h)
        lines = []

    // override paint to do custom drawing
    //
    def paint(x)
        for line in lines
            draw_line(line[0], line[1], line[2], line[3])

    // override handle to handle mouse events
    //
    def handle(event, x, y)
        var line
        if event == WXS_LEFT_DOWN
            if mouse_is_down
                return
            line = [x, y, x, y]
            lines.append(line)
            mouse_is_down = true
        elif event == WXS_MOVE and mouse_is_down
            // change the end-point of the last line to follow the mouse
            line = lines.last()
            line[2] = x
            line[3] = y
        // It might be possible to receive a mouse up without a mouse down
        // E.g. the mouse down might be captured by the window system to
        // change the focus to this canvas, and the mouse down might not
        // be delivered to the canvas. In that case, ignore the mouse-up
        // event because we have not received a mouse down yet.
        elif event == WXS_LEFT_UP and mouse_is_down
            line = lines.last()
            line[2] = x
            line[3] = y
            mouse_is_down = false
        else // could be keyboard input
            return // no state change, so return
        // State has changed. Request redraw.
        refresh(true)

// create a canvas to draw on
drawing = Drawing(WXS_DEFAULT_WINDOW, 0, 0, 200, 200)



```

```

require "debug"
require "wxserpent"

// create a subclass of Canvas -- you need to subclass Canvas in
// order to override the paint() method, which is how you make
// custom graphics
//
class Drawing (Canvas)
    // the state is an array of lines, where each line is an array
    // of x1, y1, x2, y2 coordinates for the endpoints of lines
    var lines
    var mouse_is_down

    // override init() in order to intialize the state of this
    // subclass, but pass the usuall parent, x, y, w, h parameters
    // to the init() method defined in the Canvas class so that
    // the Canvas state is also initialized.
    //
    def init(parent, x, y, w, h)
        super.init(parent, x, y, w, h)
        lines = []

    // override paint to do custom drawing
    //
    def paint(x)
        for line in lines
            draw_line(line[0], line[1], line[2], line[3])

    // override handle to handle mouse events
    //
    def handle(event, x, y)
        var line
        if event == WXS_LEFT_DOWN
            if mouse_is_down
                return
            line = [x, y, x, y]
            lines.append(line)
            mouse_is_down = true
        elif event == WXS_MOVE and mouse_is_down
            // change the end-point of the last line to follow the mouse
            line = lines.last()
            line[2] = x
            line[3] = y
        // It might be possible to receive a mouse up without a mouse down
        // E.g. the mouse down might be captured by the window system to
        // change the focus to this canvas, and the mouse down might not
        // be delivered to the canvas. In that case, ignore the mouse-up
        // event because we have not received a mouse down yet.
        elif event == WXS_LEFT_UP and mouse_is_down
            line = lines.last()
            line[2] = x
            line[3] = y
            mouse_is_down = false
        else // could be keyboard input
            return // no state change, so return
        // State has changed. Request redraw.
        refresh(true)

// create a canvas to draw on
drawing = Drawing(WXS_DEFAULT_WINDOW, 0, 0, 200, 200)



```

## Resizing Windows

### Introduction

 This example program places a canvas in a window. When the
          window is resized, the canvas is resized in order to fill the
          window. The canvas draws text that displays the canvas size.


### The Code

```

require "debug"
require "wxserpent"

class My_window (Window):
    var canvas
    
    def init(title, x, y, w, h):
        super.init(title, x, y, w, h)
        canvas = My_canvas(this.id, 0, 0, w, h)
        canvas.refresh(t)

    def on_size(x, y)
        display "on_size", x, y
        canvas.set_size(x, y)
        canvas.refresh(t)

// create a subclass of Canvas
class My_canvas (Canvas)
    def paint(flag):
        var x = get_width()
        var y = get_height()
        draw_text(30, 3, "(" + str(x) + ", " + str(y) + ")")
        // draw an arrow pointing to lower right corner
        draw_line(0, 0, x, y)
        draw_line(x - 30, y - 15, x, y)
        draw_line(x - 15, y - 30, x, y)

my_window = My_window("Resizable Window With Canvas", 100, 100, 400, 400)


```

```

require "debug"
require "wxserpent"

class My_window (Window):
    var canvas
    
    def init(title, x, y, w, h):
        super.init(title, x, y, w, h)
        canvas = My_canvas(this.id, 0, 0, w, h)
        canvas.refresh(t)

    def on_size(x, y)
        display "on_size", x, y
        canvas.set_size(x, y)
        canvas.refresh(t)

// create a subclass of Canvas
class My_canvas (Canvas)
    def paint(flag):
        var x = get_width()
        var y = get_height()
        draw_text(30, 3, "(" + str(x) + ", " + str(y) + ")")
        // draw an arrow pointing to lower right corner
        draw_line(0, 0, x, y)
        draw_line(x - 30, y - 15, x, y)
        draw_line(x - 15, y - 30, x, y)

my_window = My_window("Resizable Window With Canvas", 100, 100, 400, 400)


```

## Open Sound Control with O2

### Introduction

```

osc

```

```

o2_initialize()

```

 The server is created using o2_osc_port_new()
          which can listen on a TCP or a UDP port. The client is created
          using o2_osc_delgate() which creates an O2
          service that forwards incoming messages to an OSC server.


```

o2_osc_delgate()

```

The following is a simple OSC client.


### The Code

```

def startup()
    o2_initialize("o2osc", t) // string is the O2 application name, t for debug
    // parameters are: service name, IP address (string), port (int), use TCP flag
    o2_osc_delegate("oscsend", "localhost", 7770, false) // use UDP

def send_afloat()
    o2_send_start()
    o2_add_float(3.14159)
    // parameters are: timestamp (0 for now), address (note that it starts with
    //  the service name, and reliable (tcp) transmission flag (in this case,
    //  the ultimate transmission is controlled by the flag to o2_osc_delegate,
    //  which says send via UDP to the OSC server. The OSC server is probably
    //  using UDP; if so, you must delegate via UDP or you'll never connect.
    o2_send_finish(0.0, "/oscsend/afloat", false)


def runit()
    startup()
    while true
        send_afloat()
        time_sleep(3.0)


runit()


```

```

def startup()
    o2_initialize("o2osc", t) // string is the O2 application name, t for debug
    // parameters are: service name, IP address (string), port (int), use TCP flag
    o2_osc_delegate("oscsend", "localhost", 7770, false) // use UDP

def send_afloat()
    o2_send_start()
    o2_add_float(3.14159)
    // parameters are: timestamp (0 for now), address (note that it starts with
    //  the service name, and reliable (tcp) transmission flag (in this case,
    //  the ultimate transmission is controlled by the flag to o2_osc_delegate,
    //  which says send via UDP to the OSC server. The OSC server is probably
    //  using UDP; if so, you must delegate via UDP or you'll never connect.
    o2_send_finish(0.0, "/oscsend/afloat", false)


def runit()
    startup()
    while true
        send_afloat()
        time_sleep(3.0)


runit()


```

### The Code

```

def osc_handler(timestamp, path, types, rest parameters)
    display "osc_handler", timestamp, path, types, parameters

def startup()
    // note that the first parameter can be any application name -- it does
    //    not have to match that of the sender
    display "oscserver", o2_initialize("o2osc", t)
    display "oscserver", o2_service_new("oscrecv") // create service
    // attach a handler to the service, parameters are the path to handle,
    // the types expected, the handler (function name, a symbol), and coerce
    // flag that tells O2 to convert to the specified type(s) if possible
    display "oscserver", o2_method_new("/oscrecv/afloat", "f", 'osc_handler', true)
    // create receive port for OSC messages, which are forwarded to the service
    //    named by the first parameter. Port number is 7770, and false means UDP.

    display "oscserver", o2_osc_port_new("oscrecv", 7770, false)



def runit()
    startup()
    while true
        o2_poll()
        time_sleep(0.1)

runit()


```

```

def osc_handler(timestamp, path, types, rest parameters)
    display "osc_handler", timestamp, path, types, parameters

def startup()
    // note that the first parameter can be any application name -- it does
    //    not have to match that of the sender
    display "oscserver", o2_initialize("o2osc", t)
    display "oscserver", o2_service_new("oscrecv") // create service
    // attach a handler to the service, parameters are the path to handle,
    // the types expected, the handler (function name, a symbol), and coerce
    // flag that tells O2 to convert to the specified type(s) if possible
    display "oscserver", o2_method_new("/oscrecv/afloat", "f", 'osc_handler', true)
    // create receive port for OSC messages, which are forwarded to the service
    //    named by the first parameter. Port number is 7770, and false means UDP.

    display "oscserver", o2_osc_port_new("oscrecv", 7770, false)



def runit()
    startup()
    while true
        o2_poll()
        time_sleep(0.1)

runit()


```

## Open Sound Control

### Introduction

 The server prepares for messages by registering address
          strings using osc_server_method(). This associates
          an address string with a type string denoting the expected
          number and types of values, an object to handle the message,
          and a method to invoke.


The following is a simple OSC client.


### The Code

```

def startup()
    addr = osc_create_address("", "7770", false)

def send_afloat()
    osc_send_start()
    osc_add_float(3.14159)
    osc_send(addr, "/afloat")

def runit()
    startup()
    while true
        send_afloat()
        time_sleep(3.0)

runit()

```

```

def startup()
    addr = osc_create_address("", "7770", false)

def send_afloat()
    osc_send_start()
    osc_add_float(3.14159)
    osc_send(addr, "/afloat")

def runit()
    startup()
    while true
        send_afloat()
        time_sleep(3.0)

runit()

```

### The Code

```

def osc_handler(path, rest parameters)
    display "osc_handler", path, parameters

def startup()
    display "osctest", osc_server_init("7770", t)
    display "osctest", osc_server_method("/afloat", "f", nil, 'osc_handler')


def runit()
    startup()
    while true
        osc_server_poll()
        time_sleep(0.1)

runit()


```

```

def osc_handler(path, rest parameters)
    display "osc_handler", path, parameters

def startup()
    display "osctest", osc_server_init("7770", t)
    display "osctest", osc_server_method("/afloat", "f", nil, 'osc_handler')


def runit()
    startup()
    while true
        osc_server_poll()
        time_sleep(0.1)

runit()


```

## ZeroMQ

### Introduction 

 Here is an example of a client and server, which you would
          normally run in separate processes. By changing the address
          from "localhost" to an Internet address in the client, e.g.
          "192.168.1.39", you can connect to a server over the Internet.
          Notice that the server uses zmq_open_reply() to get
          a socket, and the server generates one zmq_send()
          call for each zmq_receive(). The client uses zmq_open_request()
          to get a socket and follows each zmq_send() with a zmq_recv_block().


### The server code:

```

def main()
    zmq_init() // prepare to use zmq
    var socket = zmq_open_reply()
    display "bind step", zmq_bind(socket, "tcp", "*", 5555)
    for i = 0 to 10
        var req = zmq_recv_block(socket)
        print "Server:", req, "-> World"
        zmq_send(socket, "World")
    zmq_close(socket)
    zmq_term()
    
main()
exit()



```

```

def main()
    zmq_init() // prepare to use zmq
    var socket = zmq_open_reply()
    display "bind step", zmq_bind(socket, "tcp", "*", 5555)
    for i = 0 to 10
        var req = zmq_recv_block(socket)
        print "Server:", req, "-> World"
        zmq_send(socket, "World")
    zmq_close(socket)
    zmq_term()
    
main()
exit()



```

### The client code:

```

def main()
    zmq_init() // prepare to use zmq
    var socket = zmq_open_request()
    display "connect step", zmq_connect(socket, "tcp", "localhost", 5555)
    for i = 0 to 10
        zmq_send(socket, "Hello")
        var result = zmq_recv_block(socket)
        print "Client: Hello ->", result
    zmq_close(socket)
    zmq_term()

main()
exit()



```

```

def main()
    zmq_init() // prepare to use zmq
    var socket = zmq_open_request()
    display "connect step", zmq_connect(socket, "tcp", "localhost", 5555)
    for i = 0 to 10
        zmq_send(socket, "Hello")
        var result = zmq_recv_block(socket)
        print "Client: Hello ->", result
    zmq_close(socket)
    zmq_term()

main()
exit()



```

### More ZeroMQ

ZeroMQ assumes that communication patterns are regular. The
          Request/Reply pattern illustrated by the client/server code
          above is one example. Other patterns supported by ZeroMQ are
          the Push/Pull pattern, where a sender produces messages that
          are consumed by a receiver, and the Publish/Subscribe pattern,
          where messages are "broadcast" to any number of receivers that
          can selectively receive messages by topic. Examples of these
          can be found in serpent/programs/zmq*.srp. Some details on the
          corresponding functions can be found in the Serpent
          documentation. Most of these functions correspond closely to
          the ZeroMQ API for the C programming language, and extensive
          ZeroMQ documentation is available online. 

## On Quit/Close

### Introduction

When a program exits or a window closes, you may want to
          prompt the user to save data or perform other cleanup actions.
          In the following little program, a handler is installed for
          the File:Quit menu item and another handler is installed for
          the default window.


The quit_handler for the File:Quit menu is only
          called when Quit is selected. The handler pops up a dialog box
          to get confirmation from the user. If the user clicks "yes,"
          we want to really quit. However, since Quit is "handled" in
          this code, wxserpent does not normally pass the event on to
          the built-in handler which will actually exit the application.
          To get wxserpent to invoke the built-in handler, we have to
          tell wxserpent explicitly that this event was not handled.
          This is accomplished by calling wxs_event_not_handled().
          Note that we only call wxs_event_not_handled() if
          the user answers "yes" in the dialog box.


The win_handler handles every event to the
          window that is not first captured by some component within the
          window. We are only interested in the WXS_CLOSE_WINDOW event,
          so we test for it. When found, we use the same strategy as quit_handler:
          get confirmation with a dialog box, and if the user really
          wants to close, use wxs_event_not_handled() to tell
          wxserpent to pass the event on to the built-in close-window
          event handler.


### The Code

```

require "debug"
require "wxserpent"

win = default_window
win.method = 'win_handler'

file_menu = win.get_menu("File")
// parameters are Menu item name, Help string, Checkable, Target, Method:
file_menu.item("Quit", "quit the application", nil, nil, 'quit_handler')

display "file quit", file_menu.map, file_menu.menu

def quit_handler(obj, event, x, y):
    display "quit_handler", obj, event, x, y
    var quit = wxs_message_box("Do you really want to quit?",
                               "Quit selected", WXS_STYLE_YES_NO, win.id)
    display "message box returns", quit, WXS_MSG_NO, WXS_MSG_YES
    // The default is that this handler performed the request, so no
    // further action (e.g. really quit the application) is performed.
    // We override this default by calling wxs_event_not_handled().
    if quit == WXS_MSG_YES:
        wxs_event_not_handled()

def win_handler(obj, event, x, y):
    display "win_handler", obj, event, x, y, WXS_CLOSE_WINDOW
    if event == WXS_CLOSE_WINDOW:
        var close = wxs_message_box("Do you really want to close?",
                               "Close", WXS_STYLE_YES_NO, win.id)
        if close == WXS_MSG_YES:
            wxs_event_not_handled()


```

```

require "debug"
require "wxserpent"

win = default_window
win.method = 'win_handler'

file_menu = win.get_menu("File")
// parameters are Menu item name, Help string, Checkable, Target, Method:
file_menu.item("Quit", "quit the application", nil, nil, 'quit_handler')

display "file quit", file_menu.map, file_menu.menu

def quit_handler(obj, event, x, y):
    display "quit_handler", obj, event, x, y
    var quit = wxs_message_box("Do you really want to quit?",
                               "Quit selected", WXS_STYLE_YES_NO, win.id)
    display "message box returns", quit, WXS_MSG_NO, WXS_MSG_YES
    // The default is that this handler performed the request, so no
    // further action (e.g. really quit the application) is performed.
    // We override this default by calling wxs_event_not_handled().
    if quit == WXS_MSG_YES:
        wxs_event_not_handled()

def win_handler(obj, event, x, y):
    display "win_handler", obj, event, x, y, WXS_CLOSE_WINDOW
    if event == WXS_CLOSE_WINDOW:
        var close = wxs_message_box("Do you really want to close?",
                               "Close", WXS_STYLE_YES_NO, win.id)
        if close == WXS_MSG_YES:
            wxs_event_not_handled()


```

## Animation Basics

## Networks: Server Creation

## Networks: Detecting Disconnects


## Networks: Message Length