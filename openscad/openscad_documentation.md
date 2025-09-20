# OpenSCAD Documentation

This document contains converted documentation from HTML files.

---

# En.Wikibooks.Org Wiki Openscad User Manual Text

# OpenSCAD User Manual — Text

The `text()` module creates text as a 2D geometric object, using fonts installed on the local system or provided as separate font files.

Note: Requires version 2015.03

## Parameters

- text: String. The text to generate.
- size: Decimal. The generated text has an ascent (height above the baseline) of approximately this value. Default is 10. Fonts vary and may be a different height, typically slightly smaller. Conversion to points: pt = size / 3.937 (e.g., size=3.05 ≈ 12 pt). Note that point measurements for text generally refer to ascent-to-descent, not ascent-to-baseline.
- font: String. Logical font name (not the font file name). May include a style parameter, e.g., `font="Liberation Sans:style=Bold Italic"`.
- halign: String. Horizontal alignment: "left", "center", "right". Default "left".
- valign: String. Vertical alignment: "top", "center", "baseline", "bottom". Default "baseline".
- spacing: Decimal. Factor to increase/decrease character spacing. Default 1.
- direction: String. Text flow: "ltr" (left-to-right), "rtl" (right-to-left), "ttb" (top-to-bottom), "btt" (bottom-to-top). Default "ltr".
- language: String. Language of the text (e.g., "en", "ar", "ch"). Default "en".
- script: String. Script of the text (e.g., "latin", "arabic", "hani"). Default "latin".
- $fn: Used for subdividing curved path segments provided by FreeType.

## Example

### Example 1

```openscad
text("OpenSCAD");
```

## Unicode and escape sequences

To allow specification of particular Unicode characters, use escape codes within strings:

- \xNN — Hex char value (01–7f)
- \uNNNN — Unicode char with 4 hex digits (lowercase u)
- \UNNNNNN — Unicode char with 6 hex digits (uppercase U)

The null character (NUL) is mapped to the space character (SP).

```openscad
assert(version() == [2019, 5, 0]);
assert(ord(" ") == 32);
assert(ord("\x00") == 32);
assert(ord("\u0000") == 32);
assert(ord("\U000000") == 32);

// Example: 10 euro and a smiley
t = "\u20AC10 \u263A";
```

## Using Fonts & Styles

Fonts are specified by logical name; a style parameter can be added to select a specific style (e.g., Bold, Italic):

```openscad
text("Sample", font="Liberation Sans:style=Bold Italic");
```

OpenSCAD includes the fonts Liberation Mono, Liberation Sans, and Liberation Serif. Using these is recommended for portability across platforms. Liberation Sans is the default.

In addition to installed fonts (on Windows, only fonts installed for all users are available), it is possible to add project-specific font files. Supported formats: TrueType (*.ttf) and OpenType (*.otf). Register font files with `use <>`:

```openscad
use <ttf/paratype-serif/PTF55F.ttf>
```

After registration, the font appears in the font list dialog and can be referenced by its logical name.

List system-configured fonts via fontconfig tools:

```
fc-list -f "%-60{{%{family[0]}%{:style[0]=}}}%{file}\n" | sort
```

On Windows, list font file names from the registry:

```
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /s > List_Fonts_Windows.txt
```

### Example 2

```openscad
square(10);

translate([15, 15]) {
  text("OpenSCAD", font = "Liberation Sans");
}

translate([15, 0]) {
  text("OpenSCAD", font = "Liberation Sans:style=Bold Italic");
}
```

## Alignment

### Vertical alignment

- top: Aligns so the top of the tallest character is at the given Y coordinate.
- center: Centers the text bounding box at the given Y coordinate.
- baseline: Aligns the font baseline at the given Y coordinate. Default. The only option that makes different text pieces align vertically like on lined paper.
- bottom: Aligns so the lowest-reaching character bottom is at the given Y coordinate.

```openscad
text = "Align";
font = "Liberation Sans";
valign = [
  [ 0,  "top"],
  [ 40, "center"],
  [ 75, "baseline"],
  [110, "bottom"]
];

for (a = valign) {
  translate([10, 120 - a[0], 0]) {
    color("red")  cube([135, 1,   0.1]);
    color("blue") cube([1,   20,  0.1]);
    linear_extrude(height = 0.5) {
      text(text = str(text, "_", a[1]),
           font = font, size = 20, valign = a[1]);
    }
  }
}
```

Notes on multi-line text:
- text() does not support multi-line content; use separate text() calls per line with translate() for spacing.
- Minimum spacing to avoid overlap with descenders: 1.4 * size.
- Approximate single-spacing (as in word processors): 1.6 * size.
- Use valign="baseline" for even line spacing regardless of character shapes.

### Horizontal alignment

- left: Aligns the left side of the bounding box at the given X coordinate. Default.
- center: Centers the text bounding box at the given X coordinate.
- right: Aligns the right side of the bounding box at the given X coordinate.

```openscad
text = "Align";
font = "Liberation Sans";
halign = [
  [10, "left"],
  [50, "center"],
  [90, "right"]
];

for (a = halign) {
  translate([140, a[0], 0]) {
    color("red")  cube([115, 2,  0.1]);
    color("blue") cube([2,   20, 0.1]);
    linear_extrude(height = 0.5) {
      text(text = str(text, "_", a[1]),
           font = font, size = 20, halign = a[1]);
    }
  }
}
```

## 3D text

Text can be turned into a 3D object using linear_extrude.

```openscad
// 3D Text Example
linear_extrude(4) text("Text");
```

## Metrics

Note: Requires version Development snapshot

### textmetrics()

The `textmetrics()` function accepts the same parameters as `text()` and returns an object describing how the text would be rendered.

Returned object members:
- position: Lower-left corner of the generated text.
- size: Size of the generated text.
- ascent: Amount extending above the baseline.
- descent: Amount extending below the baseline.
- offset: Lower-left corner of the box containing the text, including inter-glyph spacing before the first glyph.
- advance: The point where additional text should start.

```openscad
s = "Hello, World!";
size = 20;
font = "Liberation Serif";

tm = textmetrics(s, size = size, font = font);
echo(tm);

translate([0, 0, 1]) text(s, size = size, font = font);
color("black") translate(tm.position) square(tm.size);
```

Example echo output (reformatted):

```
ECHO: {
  position = [0.7936, -4.2752];
  size     = [149.306, 23.552];
  ascent   = 19.2768;
  descent  = -4.2752;
  offset   = [0, 0];
  advance  = [153.09, 0];
}
```

### fontmetrics()

The `fontmetrics()` function accepts an optional font size and font name and returns global characteristics of the font.

Parameters:
- size: Decimal, optional. As for `text()`.
- font: String, optional. As for `text()`.

Returns an object:
- nominal: Usual glyph dimensions
  - ascent: Height above baseline
  - descent: Depth below baseline
- max: Maximum glyph dimensions
  - ascent: Height above baseline
  - descent: Depth below baseline
- interline: Design distance from one baseline to the next
- font: Identification info
  - family: Font family name
  - style: Style (Regular, Italic, etc.)

```openscad
echo(fontmetrics(font = "Liberation Serif"));
```

Example echo output (reformatted):

```
ECHO: {
  nominal = { ascent = 12.3766; descent = -3.0043; };
  max     = { ascent = 13.6312; descent = -4.2114; };
  interline = 15.9709;
  font = { family = "Liberation Serif"; style = "Regular"; };
}
```

---

# En.Wikibooks.Org Wiki Openscad User Manual User-Defined Functions And Modules Children

# OpenSCAD User Manual — User-Defined Functions and Modules (Children)

Users can extend the language by defining their own functions and modules. This allows grouping portions of script for easy reuse with different values. Well-chosen names also help document your script.

- Functions return values.
- Modules perform actions and do not return values.
- OpenSCAD calculates the value of variables at compile-time, not run-time. The last variable assignment within a scope applies everywhere in that scope and in inner scopes (children). Think of them as override-able constants rather than runtime variables.
- For functions and modules, OpenSCAD makes copies of pertinent portions of the script for each use. Each copy has its own scope containing fixed values for variables and expressions unique to that instance.
- Names of functions and modules are case-sensitive: test() and TEST() are different.

## Scope

Modules and functions can be defined within a module definition, where they are visible only within that module’s scope.

```openscad
function parabola(f, x) = (1 / (4 * f)) * x * x;

module plotParabola(f, wide, steps = 1) {
  function y(x) = parabola(f, x);

  module plot(x, y) {
    translate([x, y]) circle(1, $fn = 12);
  }

  xAxis = [-wide / 2 : steps : wide / 2];
  for (x = xAxis) plot(x, y(x));
}

color("red")  plotParabola(10, 100, 5);
color("blue") plotParabola(4, 60, 2);
```

The function y() and module plot() cannot be called in the global scope.

## Functions

Function definition:

```
function name(parameters) = value;
```

Field | Description
---|---
name | Your function name. Valid characters: [a-zA-Z0-9_]
parameters | Zero or more arguments. Parameters can have default values. Parameter names are local and do not conflict with external variables of the same name.
value | An expression that calculates a value (can be scalar or vector).

### Function use

When used, functions are treated as values and do not end with a semicolon.

```openscad
// example 1
function func0()         = 5;
function func1(x = 3)    = 2 * x + 1;
function func2()         = [1, 2, 3, 4];
function func3(y = 7)    = (y == 7) ? 5 : 2;
function func4(p0, p1, p2, p3) = [p0, p1, p2, p3];

echo(func0());                    // 5
a = func1();                      // 7
b = func1(5);                     // 11
echo(func2());                    // [1, 2, 3, 4]
echo(func3(2), func3());          // 2, 5
z = func4(func0(), func1(), func2(), func3());
// z = [5, 7, [1, 2, 3, 4], 5]

translate([0, -4 * func0(), 0])
  cube([func0(), 2 * func0(), func0()]);
// same as:
// translate([0, -20, 0]) cube([5, 10, 5]);

// example 2: creates for() range to give desired number of steps
function steps(start, no_steps, end) = [start : (end - start) / (no_steps - 1) : end];

echo(steps(10, 3, 5));    // [10 : -2.5 : 5]
for (i = steps(10, 3, 5)) echo(i);  // 10 7.5 5

echo(steps(10, 3, 15));   // [10 : 2.5 : 15]
for (i = steps(10, 3, 15)) echo(i); // 10 12.5 15

echo(steps(0, 5, 5));     // [0 : 1.25 : 5]
for (i = steps(0, 5, 5)) echo(i);   // 0 1.25 2.5 3.75 5

// example 3: rectangle with top pushed over, keeping same y
function rhomboid(x = 1, y = 1, angle = 90) =
  [[0, 0],
   [x, 0],
   [x + x * cos(angle) / sin(angle), y],
   [x * cos(angle) / sin(angle), y]];

echo(v1);
v1 = rhomboid(10, 10, 35);
// [[0, 0],
//  [10, 0],
//  [24.2815, 10],
//  [14.2815, 10]]

polygon(v1);
polygon(rhomboid(10, 10, 35));

// alternate: performing the same action with a module
module parallelogram(x = 1, y = 1, angle = 90) {
  polygon([
    [0, 0],
    [x, 0],
    [x + x * cos(angle) / sin(angle), y],
    [x * cos(angle) / sin(angle), y]
  ]);
}
parallelogram(10, 10, 35);
```

You can also use let to create variables in a function:

```openscad
function get_square_triangle_perimeter(p1, p2) =
  let (hypotenuse = sqrt(p1 * p1 + p2 * p2))
    p1 + p2 + hypotenuse;
```

### Recursive functions

Recursive function calls are supported. Use the conditional operator to terminate recursion.

```openscad
// recursion example: add all integers up to n
function add_up_to(n) = (n == 0 ? 0 : n + add_up_to(n - 1));
```

There is a built-in recursion limit (a few thousands). If the limit is hit, you get an error like:
ERROR: Recursion detected calling function ...

Tail-recursion elimination is supported for tail-recursive functions:

```openscad
// tail-recursion elimination example: add all integers up to n
function add_up_to(n, sum = 0) = n == 0 ? sum : add_up_to(n - 1, sum + n);

echo(sum = add_up_to(100000));  // ECHO: sum = 5.00005e+009
```

Tail-recursion elimination allows much higher recursion limits (up to about 1,000,000).

### Function Literals

Note: Requires version 2021.01

Function literals (lambdas/closures) are expressions that define functions.

```openscad
// function literal
function (x) x + x;
```

Function literals can be assigned to variables and passed around like any value. Call them with normal function call syntax.

```openscad
func = function (x) x * x;
echo(func(5));  // ECHO: 25
```

Functions can return functions. Unbound variables are captured by lexical scope.

```openscad
a = 1;

selector = function (which)
  which == "add"
    ? function (x) x + x + a
    : function (x) x * x + a;

echo(selector("add"));      // ECHO: function(x) ((x + x) + a)
echo(selector("add")(5));   // ECHO: 11
echo(selector("mul"));      // ECHO: function(x) ((x * x) + a)
echo(selector("mul")(5));   // ECHO: 26
```

### Overwriting built-in functions

It is possible to overwrite built-in functions. Definitions are processed first, so both echoes below print true.

Source code:

```openscad
echo(sin(1));
function sin(x) = true;
echo(sin(1));
```

Console output:

```
Compiling design (CSG Tree generation)...
ECHO: true
ECHO: true
Compiling design (CSG Products generation)...
```

## Modules

Modules can be used to define objects or, using children(), define operators. Once defined, modules are temporarily added to the language.

Module definition:

```
module name(parameters) { actions }
```

Field | Description
---|---
name | Your module name. Valid characters: [a-zA-Z0-9_]
parameters | Zero or more arguments, optionally with default values. Names are local and do not conflict with external variables of the same name.
actions | Any valid statements, including definitions of functions and modules. Such nested items are only visible within the enclosing module. Variables assigned inside are scoped to each use of the module. Modules do not return values.

### Object modules

Object modules use primitives and operators to define new objects. In use, object modules are actions ending with a semicolon.

```openscad
// example 1: Color bar
translate([-30, -20, 0]) ShowColorBars(Expense);

ColorBreak = [
  [  0,   ""],
  [ 20,   "lime"],        // upper limit of color range
  [ 40,   "greenyellow"],
  [ 60,   "yellow"],
  [ 75,   "LightCoral"],
  [200,   "red"]
];

Expense = [16, 20, 25, 85, 52, 63, 45];

module ColorBar(value, period, range) { // 1 color on 1 bar
  RangeHi = ColorBreak[range][0];
  RangeLo = ColorBreak[range - 1][0];

  color(ColorBreak[range][1])
    translate([10 * period, 0, RangeLo])
      if (value > RangeHi)
        cube([5, 2, RangeHi - RangeLo]);
      else if (value > RangeLo)
        cube([5, 2, value - RangeLo]);
}

module ShowColorBars(values) {
  for (month = [0 : len(values) - 1], range = [1 : len(ColorBreak) - 1])
    ColorBar(values[month], month, range);
}
```

```openscad
// example 2: House
module house(roof = "flat", paint = [1, 0, 0]) {
  color(paint)
    if (roof == "flat") {
      translate([0, -1, 0]) cube();
    } else if (roof == "pitched") {
      rotate([90, 0, 0])
        linear_extrude(height = 1)
          polygon(points = [[0,0], [0,1], [0.5,1.5], [1,1], [1,0]]);
    } else if (roof == "domical") {
      translate([0, -1, 0]) {
        translate([0.5, 0.5, 1]) sphere(r = 0.5, $fn = 20);
        cube();
      }
    }
}

house();
translate([2, 0, 0]) house("pitched");
translate([4, 0, 0]) house("domical", [0, 1, 0]);
translate([6, 0, 0]) house(roof = "pitched", paint = [0, 0, 1]);
translate([0, 3, 0]) house(paint = [0, 0, 0], roof = "pitched");
translate([2, 3, 0]) house(roof = "domical");
translate([4, 3, 0]) house(paint = [0, 0.5, 0.5]);
```

```openscad
// example 3: Coaster data
element_data = [
  [0, "",         "",   0],       // must be in order
  [1, "Hydrogen", "H",  1.008],   // indexed via atomic number
  [2, "Helium",   "He", 4.003]    // redundant atomic number to preserve sanity later
];

Hydrogen = 1;
Helium   = 2;

module coaster(atomic_number) {
  element      = element_data[atomic_number][1];
  symbol       = element_data[atomic_number][2];
  atomic_mass  = element_data[atomic_number][3];
  // rest of script
}
```

### Operator modules

#### Children

Use of children() allows modules to act as operators applied to any or all of the objects within the module instantiation. In use, operator modules do not end with a semicolon.

```
name(parameter values) { scope of operator }
```

Basic use: apply a modification to the scoped children.

```openscad
module myModification() {
  rotate([0, 45, 0]) children();
}

myModification()  // The modification
{                 // Begin focus
  cylinder(10, 4, 4);          // First child
  cube([20, 2, 2], true);      // Second child
}                 // End focus
```

Objects are indexed via integers from 0 to $children - 1. OpenSCAD sets $children to the total number of objects within the scope. Objects grouped into a sub-scope are treated as one child. Note that children(), echo(), and empty block statements (including ifs) count as $children objects, even if no geometry is present.

Form | Description
---|---
children(); | All children
children(index); | Select one child by index
children([start : step : end]); | Range from start to end with step
children([start : end]); | Range with implicit step (1 or -1)
children([vector]); | Selection of several children by indices

Deprecated child() mapping (2013.06 and earlier):

Up to 2013.06 | 2014.03 and later
---|---
child() | children(0)
child(x) | children(x)
for (a = [0 : $children - 1]) child(a) | children([0 : $children - 1])

Examples:

```openscad
// Use all children
module move(x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0) {
  translate([x, y, z]) rotate([rx, ry, rz]) children();
}

move(10)                    cube(10, true);
move(-10)                   cube(10, true);
move(z = 7.07,  ry = 45)    cube(10, true);
move(z = -7.07, ry = 45)    cube(10, true);
```

```openscad
// Use only the first child, multiple times
module lineup(num, space) {
  for (i = [0 : num - 1])
    translate([space * i, 0, 0]) children(0);
}

lineup(5, 65) {
  sphere(30);
  cube(35);
}
```

```openscad
// Separate action for each child
module SeparateChildren(space) {
  for (i = [0 : 1 : $children - 1])           // step needed if $children < 2
    translate([i * space, 0, 0]) {
      children(i);
      text(str(i));
    }
}

SeparateChildren(-20) {
  cube(5);                       // 0
  sphere(5);                     // 1
  translate([0, 20, 0]) {        // 2
    cube(5);
    sphere(5);
  }
  cylinder(15);                  // 3
  cube(8, true);                 // 4
}

translate([0, 40, 0]) color("lightblue")
  SeparateChildren(20) { cube(3, true); }
```

```openscad
// Multiple ranges
module MultiRange() {
  color("lightblue")  children([0 : 1]);
  color("lightgreen") children([2 : $children - 2]);
  color("lightpink")  children($children - 1);
}

MultiRange() {
  cube(5);                       // 0
  sphere(5);                     // 1
  translate([0, 20, 0]) {        // 2
    cube(5);
    sphere(5);
  }
  cylinder(15);                  // 3
  cube(8, true);                 // 4
}
```

### Further module examples

Objects:

```openscad
module arrow() {
  cylinder(10);
  cube([4, 0.5, 3], true);
  cube([0.5, 4, 3], true);
  translate([0, 0, 10]) cylinder(4, 2, 0, true);
}

module cannon() {
  difference() {
    union() { sphere(10); cylinder(40, 10, 8); }
    cylinder(41, 4, 4);
  }
}

module base() {
  difference() {
    cube([40, 30, 20], true);
    translate([0, 0, 5]) cube([50, 20, 15], true);
  }
}
```

Operators — Rotary Clusters:

```openscad
module aim(elevation, azimuth = 0) {
  rotate([0, 0, azimuth]) {
    rotate([0, 90 - elevation, 0]) children(0);
    children([1 : 1 : $children - 1]);   // step needed if $children < 2
  }
}

aim(30, 20) arrow();
aim(35, 270) cannon();
aim(15) { cannon(); base(); }

module RotaryCluster(radius = 30, number = 8)
  for (azimuth = [0 : 360 / number : 359])
    rotate([0, 0, azimuth])
      translate([radius, 0, 0]) {
        children();
        translate([40, 0, 30]) text(str(azimuth));
      }

RotaryCluster(200, 7) color("lightgreen") aim(15) { cannon(); base(); }
rotate([0, 0, 110]) RotaryCluster(100, 4.5) aim(35) cannon();
color("LightBlue") aim(55, 30) { cannon(); base(); }
```

### Recursive modules

Like functions, modules may contain recursive calls. There is no tail-recursion elimination for modules. The code below generates a simple tree. Keep recursion depth n below about 7 as the number of primitives grows exponentially.

```openscad
// A simple tree created with a recursive OpenSCAD module
module simple_tree(size, dna, n) {
  if (n > 0) {
    // trunk
    cylinder(r1 = size / 10, r2 = size / 12, h = size, $fn = 24);

    // branches
    translate([0, 0, size])
      for (bd = dna) {
        angx = bd[0];
        angz = bd[1];
        scal = bd[2];
        rotate([angx, 0, angz])
          simple_tree(scal * size, dna, n - 1);
      }
  } else {
    // leaves
    color("green")
      scale([1, 1, 3])
        translate([0, 0, size / 6])
          rotate([90, 0, 0])
            cylinder(r = size / 6, h = size / 10);
  }
}

// dna is a list of branching data bd of the tree:
// bd[0] - inclination of the branch
// bd[1] - Z rotation angle of the branch
// bd[2] - relative scale of the branch
dna = [
  [12,  80, 0.85],
  [55,   0, 0.60],
  [62, 125, 0.60],
  [57, -125, 0.60]
];

simple_tree(50, dna, 5);
```

Another example of a recursive module may be found in Tips and Tricks.

### Overwriting built-in modules

It is possible to overwrite built-in modules.

```openscad
module sphere() { square(); }
sphere();
```

Note that the built-in sphere module cannot be called once overwritten.

A common pattern is to overwrite 3D primitives with extruded 2D primitives to customize default parameters and add additional parameters.

---

# En.Wikibooks.Org W Index.Php Title Openscad User Manual Mathematical Operators Scalar Arithmetical Operators

# OpenSCAD User Manual — Mathematical Operators

The scalar and vector operators below define how OpenSCAD evaluates arithmetic, relational, logical, and matrix operations. Examples are provided as OpenSCAD code blocks.

## Scalar arithmetic operators

The scalar arithmetic operators take numbers as operands and produce a new number.

| Operator | Description | Notes |
|---|---|---|
| + | add | |
| - | subtract | Also used as a prefix to negate a number |
| * | multiply | |
| / | divide | |
| % | modulo | |
| ^ | exponent | Requires version 2021.01. Prior to 2021.01, use pow() |

Example:
```openscad
a = [ for (i = [0:10]) i % 2 ];
echo(a); // ECHO: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
```
A number modulo 2 is zero if even and one if odd.

## Binary arithmetic (bitwise)

Note: Requires a development snapshot version.

| Operator | Description |
|---|---|
| | | OR |
| & | AND |
| << | Left shift |
| >> | Right shift (sign preserving) |
| ~ | Unary NOT |

Details:
- Numbers are converted to 64-bit signed integers for binary arithmetic, then converted back.
- OpenSCAD numbers have 53 bits of precision; binary arithmetic exceeding 2^53 will be imprecise.

## Relational operators

Relational operators produce a boolean result from two operands.

| Operator | Description |
|---|---|
| < | less than |
| <= | less or equal |
| == | equal |
| != | not equal |
| >= | greater or equal |
| > | greater than |

Behavior by type:
- Numbers: standard numeric comparison.
- Strings: alphabetical order determines equality and order (e.g., "ab" > "aa" > "a").
- Booleans: true > false. In comparisons between a Boolean and a number, true is 1 and false is 0. Other inequality tests involving Booleans return false.
- Vectors: equality is true only if vectors are identical; all inequality comparisons with one or two vectors return false (e.g., [1] < [2] is false).
- Dissimilar types: always unequal for == and !=; inequality comparisons (<, <=, >, >=) return false, except Boolean vs number as noted.
- Note that [1] and 1 are different types, so [1] == 1 is false.
- undef equals only undef. Inequality comparisons involving undef return false.
- nan does not equal anything (not even itself). All inequality tests with nan produce false.

## Logical operators

All logical operators take Booleans as operands and produce a Boolean. Non-Boolean operands are converted to Booleans before evaluation.

| Operator | Description |
|---|---|
| && | logical AND |
| || | logical OR |
| ! | logical unary NOT |

Notes:
- Since [false] is true (non-empty vectors are truthy), the expression false || [false] is also true.
- Logical operators treat vectors differently than relational operators: [1, 1] > [0, 2] is false, but [false, false] && [false, false] is true.

## Conditional operator

The ?: operator conditionally evaluates one of two expressions, like in C-like languages.

Usage example:
```openscad
a = 1;
b = 2;
c = (a == b) ? 4 : 5;
// If a equals b, c = 4; otherwise c = 5.
```
The test expression (a == b) must evaluate to a boolean.

## Vector-number operators

The vector-number operators take a vector and a number as operands and produce a new vector.

| Operator | Description |
|---|---|
| * | multiply all vector elements by a number |
| / | divide all vector elements by a number |

Example:
```openscad
L = [1, [2, [3, "a"]]];
echo(5 * L); // ECHO: [5, [10, [15, undef]]]
```

## Vector operators

The vector operators take vectors as operands and produce a new vector.

| Operator | Description |
|---|---|
| + | add element-wise |
| - | subtract element-wise; as a prefix, element-wise negate |

Example:
```openscad
L1 = [1, [2, [3, "a"]]];
L2 = [1, [2, 3]];
echo(L1 + L1); // ECHO: [2, [4, [6, undef]]]
echo(L1 + L2); // ECHO: [2, [4, undef]]
```
Using + or - with vector operands of different sizes produces a result vector with the size of the smaller vector.

## Vector dot-product operator

If both operands of multiplication are simple vectors, the result is a number per the dot product:
- c = u * v equals sum over i of u_i * v_i.
- If the operand sizes do not match, the result is undef.

## Matrix multiplication

If one or both operands of multiplication are matrices, the result follows standard linear algebra rules.

Let A be n×m and B be m×p:
- C = A * B is n×p with elements: C_ij = sum over k=0..m-1 of A_i,k * B_k,j.
- B * A is defined only if p = n; otherwise the result is undef.

Matrix–vector products:
- For A (n×m) and v (size m): u = A * v is a vector of size n with u_i = sum over k=0..m-1 of A_i,k * v_k.
- For v (size n) and A (n×m): u = v * A is a vector of size m with u_j = sum over k=0..n-1 of v_k * A_k,j.

Matrix multiplication is not commutative:
- A * B ≠ B * A
- A * v ≠ v * A

---

# En.Wikibooks.Org Wiki Openscad User Manual Include Statement

# OpenSCAD User Manual: Include Statement

For including code from external files in OpenSCAD, there are two commands:

- include <filename> — acts as if the contents of the included file were written at that point in the including file.
- use <filename> — imports modules and functions without executing any top-level module invocations.

Library files are searched in:
- The same folder as the design file.
- The library folder of the OpenSCAD installation.
- Folders specified by the OPENSCADPATH environment variable.

You may use relative paths. If files are elsewhere, provide the full path. Wildcards (for example, include <MCAD/*.scad>) cannot be used. Newer versions have predefined user library locations.

## include <filename>

When file A includes file B, it is almost exactly as if B were inserted at that point in A. Everything in B is visible to A, and everything in A is visible to B.

### Variables in included files

OpenSCAD variables typically have a single value; reassigning normally triggers a warning, and the last assignment is used. Inclusion is a special exception: if B defines a variable and A later assigns a value to it, the warning is suppressed and A’s value is used throughout the variable’s life. This allows library files to provide defaults that the main file can override.

```openscad
// B.scad
v = 1;
```

```openscad
// A.scad
include <B.scad>
v = 5;
echo(v = v);
```

Produces (no warning):

```
ECHO: v = 5
```

### Caution: Order of Execution

Assignments in A are executed as if located at the original assignment location in B. If the expression depends on other variables, this can cause issues.

```openscad
// B.scad
a = 1;
b = 2;
```

```openscad
// A.scad
include <B.scad>
a = b + 1;
echo(a = a, b = b);
```

Output:

```
WARNING: Ignoring unknown variable "b" in file a.scad, line 2
WARNING: undefined operation (undefined + number) in file a.scad, line 2
ECHO: a = undef, b = 2
```

## var = include <filename>;

Because include behaves like textual insertion, you can assign the contents of an external file to a variable.

Example: data.txt contains a comma-delimited list of numbers:

```
8, 6, 3, 8, 6, 4, 5, 99, 8, 1, 3, 5
```

Import into an array:

```openscad
numlist = [ include <data.txt> ];
echo(numlist);
```

Produces:

```
ECHO: [8, 6, 3, 8, 6, 4, 5, 99, 8, 1, 3, 5]
```

Note: Importing CSV with empty fields will not work reliably, as OpenSCAD ignores empty items, leading to uneven row lengths. Preprocess CSV into a compatible format first.

Another example: a polyhedron described in cube.poly as an array of vertices and faces:

```openscad
// cube.poly
[
  [ // vertices
    [37.5,67.5,0],
    [37.5,42.5,0],
    [12.5,42.5,0],
    [12.5,67.5,0],
    [37.5,67.5,25],
    [12.5,67.5,25],
    [12.5,42.5,25],
    [37.5,42.5,25]
  ],
  [ // faces
    [3,2,1,0],
    [7,6,5,4],
    [1,7,4,0],
    [2,6,7,1],
    [3,5,6,2],
    [5,3,0,4]
  ]
]
```

Use it in OpenSCAD:

```openscad
cube_poly = include <cube.poly>;
vertices = cube_poly[0];
faces = cube_poly[1];
polyhedron(vertices, faces);
```

When assigning the contents of an included file to a variable, avoid using .scad files for data. Prefer a non-.scad extension and ensure the file contains data, not OpenSCAD source code.

## use <filename>

When file A uses file B:

- A can see B’s modules and functions.
- A cannot see B’s global variables.
- B cannot see A’s global variables.
- B cannot see A’s modules and functions.
- B’s top-level module invocations are not executed.
- B’s top-level assignments are executed on every call from A to B. This can be useful if they depend on $ variables in A, but may affect performance. This behavior is subject to change.

use <filename> is allowed only at the top level of a file.

## Example: Ring Library

Library file:

```openscad
// ring.scad
module ring(r1, r2, h) {
  difference() {
    cylinder(r = r1, h = h);
    translate([0, 0, -1])
      cylinder(r = r2, h = h + 2);
  }
}

// Example invocation inside the library:
ring(5, 4, 10);
```

Using include:

```openscad
include <ring.scad>
rotate([90, 0, 0])
  ring(10, 1, 1);
```

Result: both the example ring from the library and the rotated ring are shown.

Using use:

```openscad
use <ring.scad>
rotate([90, 0, 0])
  ring(10, 1, 1);
```

Result: only the rotated ring is shown.

## Additional Notes

### Directory separators

- Windows uses backslashes: directory\file.ext
- Linux and macOS use forward slashes: directory/file.ext

OpenSCAD on Windows accepts forward slashes, so using / in include or use statements works on all platforms.

### Nested Include and Use

OpenSCAD executes nested include and use statements. Caveat: use brings functions and modules only into the local file’s context. Modules and functions imported by a nested use are not visible to the base file; they fall out of scope before reaching the base context.

---

# En.Wikibooks.Org Wiki Openscad User Manual Primitive Solids Cube

# OpenSCAD User Manual — Primitive Solids

This document summarizes the OpenSCAD primitive solids with syntax, parameters, defaults, and examples. It focuses on technical content and complete, properly formatted OpenSCAD code.

## cube

Creates a cube or rectangular prism (box) in the first octant by default. When center is true, the cube is centered on the origin. Argument names are optional if given in the order shown.

Syntax:
```openscad
cube(size = [x, y, z], center = true/false);
cube(size = x, center = true/false);
```

Parameters:
- size:
  - Single value: cube with all sides this length
  - 3-value array [x, y, z]: rectangular prism with dimensions x, y, z
- center:
  - false (default): 1st (positive) octant, one corner at (0,0,0)
  - true: cube is centered at (0,0,0)

Defaults:
```openscad
cube();  // yields:
cube(size = [1, 1, 1], center = false);
```

Examples (equivalent scripts for a cube of size 18):
```openscad
cube(size = 18);
cube(18);
cube([18,18,18]);

cube(18,false);
cube([18,18,18],false);
cube([18,18,18],center=false);
cube(size = [18,18,18], center = false);
cube(center = false, size = [18,18,18]);
```

Examples (equivalent scripts for a box 18×28×8, centered):
```openscad
cube([18,28,8],true);
box = [18,28,8]; cube(box,true);
```

---

## sphere

Creates a sphere at the origin. The r argument name is optional. If using d (diameter) instead of r, d must be named.

Parameters:
- r: Radius of the sphere. Resolution is controlled by $fa, $fs, $fn.
- d: Diameter of the sphere (use named parameter).
- $fa: Fragment angle in degrees (minimum angle of each fragment).
- $fs: Fragment size in mm (minimum circumferential length).
- $fn: Fixed number of fragments in 360 degrees. Values of 3 or more override $fa and $fs.

Defaults:
```openscad
sphere();  // yields:
sphere($fn = 0, $fa = 12, $fs = 2, r = 1);
```

Usage examples:
```openscad
sphere(r = 1);
sphere(r = 5);
sphere(r = 10);

sphere(d = 2);
sphere(d = 10);
sphere(d = 20);

// high resolution sphere with a 2 mm radius
sphere(2, $fn = 100);

// also 2 mm high resolution, fewer small triangles at the poles
sphere(2, $fa = 5, $fs = 0.1);
```

---

## cylinder

Creates a cylinder or cone centered about the z-axis. When center is true, it is centered vertically along the z-axis. Parameter names are optional if given in the order shown. If a parameter is named, all following parameters must also be named.

Syntax:
```openscad
cylinder(h = height, r1 = BottomRadius, r2 = TopRadius, center = true/false);
```

Notes:
- The 2nd and 3rd positional parameters are r1 and r2. If r, d, d1, or d2 are used, they must be named.
- Using r1 & r2 or d1 & d2 with either value zero creates a cone. A non-zero, non-equal pair produces a conical frustum.
- r1/d1 define the base width at z=0; r2/d2 define the top width.

Parameters:
- h: Height of the cylinder or cone
- r: Radius of cylinder; sets r1 = r2 = r
- r1: Radius at bottom
- r2: Radius at top
- d: Diameter of cylinder; sets r1 = r2 = d/2 (requires version 2014.03 or later)
- d1: Diameter at bottom; r1 = d1/2 (requires 2014.03+)
- d2: Diameter at top; r2 = d2/2 (requires 2014.03+)
- center:
  - false (default): z ranges from 0 to h
  - true: z ranges from -h/2 to +h/2
- $fa: Minimum angle (degrees) per fragment
- $fs: Minimum circumferential length per fragment
- $fn: Fixed number of fragments; values ≥3 override $fa and $fs

Defaults:
```openscad
cylinder();  // yields:
cylinder($fn = 0, $fa = 12, $fs = 2, h = 1, r1 = 1, r2 = 1, center = false);
```

Equivalent scripts:
```openscad
cylinder(h=15, r1=9.5, r2=19.5, center=false);
cylinder(15, 9.5, 19.5, false);
cylinder(15, 9.5, 19.5);
cylinder(15, 9.5, d2=39);
cylinder(15, d1=19, d2=39);
cylinder(15, d1=19, r2=19.5);
```

Cone equivalents:
```openscad
cylinder(h=15, r1=10, r2=0, center=true);
cylinder(15, 10, 0, true);
cylinder(h=15, d1=20, d2=0, center=true);
```

Cylinder with equal radii:
```openscad
cylinder(h=20, r=10, center=true);
cylinder(20, 10, 10, true);
cylinder(20, d=20, center=true);
cylinder(20, r1=10, d2=20, center=true);
cylinder(20, r1=10, d2=2*10, center=true);
```

### Use of $fn

Larger $fn creates smoother, more circular surfaces at the cost of longer rendering time. During development, use medium values for faster preview; increase for the final render (F6). Small values can create interesting polygonal forms.

Examples:
```openscad
cylinder(20, 20, 20, $fn = 3);
cylinder(20, 20, 00, $fn = 4);
cylinder(20, 20, 10, $fn = 4);
```

### Undersized holes

Using cylinder() with difference() to place holes creates undersized holes because circles are approximated by inscribed polygons. To ensure the hole is not undersized, use a circumscribed polygon (increase radius so the polygon lies outside the circle).

Modules for circumscribed holes (example):
```openscad
poly_n = 6;

color("blue")
translate([0, 0, 0.02])
linear_extrude(0.1)
circle(10, $fn = poly_n);

color("green")
translate([0, 0, 0.01])
linear_extrude(0.1)
circle(10, $fn = 360);

color("purple")
linear_extrude(0.1)
circle(10 / cos(180 / poly_n), $fn = poly_n);
```

Regular n-gon relationships:
- For a polygon of circumradius r, the apothem (midpoint radius) rm = r * cos(180/n).
- If only the apothem rm is known (e.g., to fit a hex key), the circumradius r = rm / cos(180/n).

---

## polyhedron

The most general 3D primitive. Can create regular or irregular shapes, concave or convex. Curved surfaces are approximated by flat faces.

Syntax (before 2014.03):
```openscad
polyhedron(
  points    = [ [X0, Y0, Z0], [X1, Y1, Z1], ... ],
  triangles = [ [P0, P1, P2], ... ],
  convexity = N
);
```

Syntax (2014.03 and later):
```openscad
polyhedron(
  points = [ [X0, Y0, Z0], [X1, Y1, Z1], ... ],
  faces  = [ [P0, P1, P2, P3, ...], ... ],
  convexity = N
);
```

Parameters:
- points: Vector of 3D points [x, y, z]. Points can be defined in any order and are indexed 0..N-1.
- triangles: Deprecated (will be removed). Vector of faces, each a 3-index triangle into points.
- faces: Vector of faces, each 3 or more indices into points. Define enough faces to fully enclose the solid, with no overlap. If coplanarity is violated, faces are triangulated automatically.
- convexity: Integer specifying the maximum number of faces a ray might intersect (used for OpenCSG preview correctness only; no effect on final render). For most cases, 10 suffices.

Defaults:
```openscad
polyhedron();  // yields:
polyhedron(points = undef, faces = undef, convexity = 1);
```

Winding order:
- For each face, the listed point indices must be ordered clockwise when viewed from outside the solid. Use the left-hand rule: curl fingers along the order; thumb points outward.

### Example 1: Cube via polyhedron (10 × 7 × 5)

```openscad
CubePoints = [
  [ 0, 0, 0 ],  // 0
  [10, 0, 0 ],  // 1
  [10, 7, 0 ],  // 2
  [ 0, 7, 0 ],  // 3
  [ 0, 0, 5 ],  // 4
  [10, 0, 5 ],  // 5
  [10, 7, 5 ],  // 6
  [ 0, 7, 5 ]   // 7
];

CubeFaces = [
  [0,1,2,3],   // bottom
  [4,5,1,0],   // front
  [7,6,5,4],   // top
  [5,6,2,1],   // right
  [6,7,3,2],   // back
  [7,4,0,3]    // left
];

polyhedron(CubePoints, CubeFaces);
```

Equivalent descriptions of the bottom face:
```openscad
[0,1,2,3],
[0,1,2,3,0],
[1,2,3,0],
[2,3,0,1],
[3,0,1,2],
[0,1,2], [2,3,0],   // two triangles, no overlap
[1,2,3], [3,0,1],
[1,2,3], [0,1,3]
```

### Example 2: Square-base pyramid

```openscad
polyhedron(
  points = [
    [ 10,  10, 0], [ 10, -10, 0], [-10, -10, 0], [-10,  10, 0],  // base
    [  0,   0,10]                                                  // apex
  ],
  faces = [
    [0,1,4], [1,2,4], [2,3,4], [3,0,4],  // triangular sides
    [1,0,3], [2,1,3]                     // base (two triangles)
  ]
);
```

### Example 3: Triangular prism

```openscad
module prism(l, w, h) {
  polyhedron(
    // pt: 0  1     2     3    4    5
    points = [[0,0,0], [0,w,h], [l,w,h], [l,0,0], [0,w,0], [l,w,0]],
    faces  = [
      [0,1,2,3],  // A: top sloping face
      [2,1,4,5],  // B: vertical rectangular face
      [0,3,5,4],  // C: bottom face
      [0,4,1],    // D: rear triangular face
      [3,2,5]     // E: front triangular face
    ]
  );
}

prism(10, 10, 5);
```

---

## Debugging polyhedra

Common issues:
- Faces not in clockwise order (as viewed from outside; view bottoms from below).
- Overlapping faces.
- Missing faces or portions of faces.
- Non-manifold edges (every edge should be shared by exactly two faces; faces sharing only a vertex must be in the same face-edge cycle around that vertex).

Tips:
- In “Thrown together” view (F12) with preview (F5), counterclockwise (CCW) faces are shown in pink. Rotate to inspect all faces. Toggle pink view with F10.
- Comment out faces temporarily to isolate issues:
  - Line comments: //
  - Block comments: /* ... */

Show only two faces (example):
```openscad
CubeFaces = [
  /* [0,1,2,3],  // bottom
     [4,5,1,0],  // front */
  [7,6,5,4],    // top
  /* [5,6,2,1],  // right
     [6,7,3,2],  // back */
  [7,4,0,3]     // left
];
```

Validation tip:
- A polyhedron may preview fine but still be invalid for STL. Union it with any cube and render (F6). If it disappears, fix winding order and manifold issues.

---

## Mis-ordered faces

Bad polyhedron (faces in wrong order highlighted in “Thrown together” F5 preview):
```openscad
// Bad polyhedron
polyhedron(
  points = [
    [0, -10, 60], [0,  10, 60], [0, 10,  0], [0, -10,  0],
    [60, -10, 60], [60, 10, 60],
    [10, -10, 50], [10, 10, 50], [10, 10, 30], [10, -10, 30],
    [30, -10, 50], [30, 10, 50]
  ],
  faces = [
    [0,2,3], [0,1,2], [0,4,5], [0,5,1], [5,4,2], [2,4,3],
    [6,8,9], [6,7,8], [6,10,11], [6,11,7], [10,8,11], [10,9,8],
    [0,3,9], [9,0,6], [10,6,0], [0,4,10], [3,9,10], [3,10,4],
    [1,7,11], [1,11,5], [1,7,8], [1,8,2], [2,8,11], [2,11,5]
  ]
);
```

Corrected polyhedron:
```openscad
polyhedron(
  points = [
    [0, -10, 60], [0,  10, 60], [0, 10,  0], [0, -10,  0],
    [60, -10, 60], [60, 10, 60],
    [10, -10, 50], [10, 10, 50], [10, 10, 30], [10, -10, 30],
    [30, -10, 50], [30, 10, 50]
  ],
  faces = [
    [0,3,2], [0,2,1], [4,0,5], [5,0,1], [5,2,4], [4,2,3],
    [6,8,9], [6,7,8], [6,10,11], [6,11,7], [10,8,11], [10,9,8],
    [3,0,9], [9,0,6], [10,6,0], [0,4,10], [3,9,10], [3,10,4],
    [1,7,11], [1,11,5], [1,8,7], [2,8,1], [8,2,11], [5,11,2]
  ]
);
```

Beginner’s tip:
- Identify pink mis-oriented faces, then reverse their index order. Example: [0,4,5] becomes [4,0,5]. Face lists are circular; other clockwise permutations like [5,4,0] or [0,5,4] are also valid.

Clockwise technique (left-hand rule):
- With your left hand on the face, curl fingers in the order of the points. Your thumb should point outward. If not, reverse the order.

Succinct polyhedron description:
- points: list of vertices [x, y, z], auto-indexed from 0.
- faces: list of polygons by vertex indices (3 or more).
- Faces must list indices in clockwise order when viewed from outside.

---

## Point repetitions in a polyhedron point list

Duplicate coordinates in the points list are treated as the same vertex.

Equivalent definitions of the same tetrahedron:

With repetitions:
```openscad
points = [
  [ 0, 0, 0], [10, 0, 0], [ 0,10, 0],
  [ 0, 0, 0], [10, 0, 0], [ 0,10, 0],
  [ 0,10, 0], [10, 0, 0], [ 0, 0,10],
  [ 0, 0, 0], [ 0, 0,10], [10, 0, 0],
  [ 0, 0, 0], [ 0,10, 0], [ 0, 0,10]
];

polyhedron(points, [
  [0,1,2], [3,4,5], [6,7,8], [9,10,11], [12,13,14]
]);
```

Simplified:
```openscad
points = [
  [0,0,0], [0,10,0], [10,0,0], [0,0,10]
];

polyhedron(points, [
  [0,2,1], [0,1,3], [1,2,3], [0,3,2]
]);
```

---

# En.Wikibooks.Org Wiki Openscad User Manual General Dot Notation Indexing

# OpenSCAD User Manual — General

OpenSCAD is a 2D/3D solid modeling program based on a functional programming language. A script in the OpenSCAD language creates 2D/3D models, previewed on screen and rendered to meshes exportable to various formats.

A script is a free-form list of action statements.

```openscad
object();
variable = value;

operator() action();

operator() {
  action();
  action();
}

operator()
operator() {
  action();
  action();
}

operator() {
  operator() action();
  operator() {
    action();
    action();
  }
}
```

## Objects

Objects are the building blocks for models, created by 2D/3D primitives. Objects end with a semicolon.

Examples: cube(), sphere(), polygon(), circle(), etc.

## Actions

Action statements include creating objects using primitives and assigning values to variables. Action statements end with a semicolon.

```openscad
a = 1;
b = a + 7;
```

## Operators

Operators (transformations) modify location, color, and other properties. Braces {} group multiple actions. Multiple operators are processed right-to-left (closest to the action applies first). Operators do not end with semicolons; actions inside them do.

```openscad
cube(5);
x = 4 + y;

rotate(40) square(5, 10);

translate([10, 5]) {
  circle(5);
  square(4);
}

rotate(60) color("red") {
  circle(5);
  square(4);
}

color("blue") {
  translate([5, 3, 0]) sphere(5);
  rotate([45, 0, 45]) {
    cylinder(10);
    cube([5, 6, 7]);
  }
}
```

## Comments

Comments are ignored by the compiler.

```openscad
// This is a comment
myvar = 10;  // The rest of the line is a comment

/* Multi-line comments
   can span multiple lines. */
```

## Values and Data Types

A value in OpenSCAD is one of:
- Number (e.g., 42)
- Boolean (true, false)
- String (e.g., "foo")
- Range (e.g., [0: 1: 10])
- Vector (e.g., [1, 2, 3])
- Undefined (undef)

OpenSCAD is dynamically typed. No user-defined types.

### Numbers

Numbers are written in decimal (e.g., -1, 42, 0.5, 2.99792458e+8). Hexadecimal constants use C-style 0x... (no octal).

OpenSCAD uses a single numeric type: 64-bit IEEE floating-point.

Implications:
- Binary floating-point cannot represent most decimals exactly. 0.25 (1/4) and 0.375 (3/8) are exact; 0.2 (2/10) is not.
- Largest magnitude is about 1e308 (inf on overflow). Smallest negative is about -1e308 (-inf on underflow).
- Precision ~16 decimal digits.
- Invalid operations can produce NaN (nan).
- Zero and negative zero (-0) are distinct in some math operations and echoed differently, but compare equal.
- inf and nan are not literal constants; they can be computed:

```openscad
inf = 1e200 * 1e200;
nan = 0 / 0;
echo(inf, nan);  // ECHO: inf, nan
```

nan is not equal to any value, including itself. To test for nan:

```openscad
x = 0/0;
echo(x != x);  // true if x is nan
```

To test for undefined:

```openscad
x = undef;
echo(x == undef);  // true
```

### Boolean values

Booleans are true or false. Non-Boolean values are converted to Boolean in contexts like if(), ?:, and logical operators.

Values that count as false:
- false
- 0 and -0
- ""
- []
- undef

Examples that count as true:
- "false"
- [0]
- [[]]
- [false]
- 0/0 (nan)

### Strings

Strings are sequences of unicode characters. Used for filenames, echo debugging, and with text().

String literal escapes:
- \" → "
- \\ → \
- \t → tab
- \n → newline
- \r → carriage return
- \xNN → ASCII (01–7F); \x00 produces a space
- \uNNNN → 4-digit Unicode
- \UNNNNNN → 6-digit Unicode

```openscad
echo("The quick brown fox \tjumps \"over\" the lazy dog.\rThe quick brown fox.\nThe \\lazy\\ dog.");
// ECHO: "The quick brown fox jumps "over" the lazy dog. The quick brown fox. The \lazy\ dog."
```

### Ranges

Ranges are used by for() and children(). They are not vectors.

Forms:
- [start:end]
- [start:step:end]  (step defaults to 1)

```openscad
r1 = [0:10];
r2 = [0.5:2.5:20];
echo(r1);  // ECHO: [0: 1: 10]
echo(r2);  // ECHO: [0.5: 2.5: 20]
```

Notes:
- [start:end] with start > end (versions ≤ 2021.01) issues a warning and is equivalent to [end:1:start]. [start:1:end] with start > end is equivalent to [] without warning. This also applies when the increment is omitted (development snapshots).
- Step may be negative (versions after 2014). If the sign of step prevents progression, the result is [] without warning.
- Use steps exactly representable in binary (integers or fractions with power-of-two denominator) to avoid off-by-one effects.

### The Undefined Value

undef is the initial value of unassigned variables and a common return for invalid operations. In logic, undef behaves as false. Relational operators return false on illegal arguments, except undef == undef is true.

Note: some numeric errors return nan (not a language value). For example:
- 0 / false → undef
- 0 / 0 → nan

## Variables

Variables bind names to expressions. Identifiers use [a-zA-Z0-9_] (development snapshots treat names starting with digits specially: 0x... is hex, others warn).

```openscad
var = 25;
xx = 1.25 * cos(50);
y  = 2 * xx + var;
logic = true;
MyString = "This is a string";
a_vector = [1, 2, 3];
rr = a_vector[2];      // 3

range1 = [-1.5:0.5:3]; // for() range
xx = [0:5];            // alternate for() range
```

OpenSCAD is functional: variables are effectively constants within a scope. Assigning a name multiple times in the same scope does not mutate; only the last assignment is used in that scope (see below).

Since 2015.03, assignments are allowed in any scope, but values cannot leak to outer scopes.

```openscad
a = 0;
if (a == 0) {
  a = 1;  // since 2015.03 allowed; value confined to this block
}
```

### Undefined variable

Referring to an undefined variable triggers a warning and yields undef. Use is_undef() to test without warnings.

```openscad
echo("Variable a is ", a);  // Triggers a warning; a is undef

if (is_undef(a)) {
  echo("Variable a is tested undefined");
}
```

### Scope of variables

Each brace pair {} creates a new inner scope. Variables defined/overridden in an inner scope are visible to deeper inner scopes but not to outer scopes.

```openscad
// scope 1
a = 6;               // create a
echo(a, b);          // 6, undef

translate([5, 0, 0]) {     // scope 1.1
  a = 10;
  b = 16;                  // create b
  echo(a, b);              // 10, 16
  a = 10;
  // ...
  color("blue") {          // scope 1.1.1
    echo(a, b);            // 10, 16
    cube();
    b = 20;
  }
  // back to 1.1
  echo(a, b);              // 10, 16
  a = 100;                 // override a in 1.1
}
// back to 1
echo(a, b);                // 6, undef

color("red") {             // scope 1.2
  cube();
  echo(a, b);              // 6, undef
}
// back to 1
echo(a, b);                // 6, undef
```

Anonymous braces alone do not create a persistent scope:

```openscad
{ angle = 45; }
rotate(angle) square(10);  // angle must be defined in a visible scope
```

for() loops create a separate scope per iteration. You still cannot write a = a + 1; to mutate a variable.

### Variables cannot be changed

Assigning the same name twice in the same scope triggers a warning; the later assignment effectively replaces the earlier at its position. The earlier assignment never executes.

```openscad
a = 1;         // never executed
echo(a);       // 2
a = 2;         // executed at the position of the original assignment
echo(a);       // 2
```

Two special non-warning cases:
- First assignment at top level of an included file, second in the including file.
- First assignment at program top level, second from -D or the Customizer.

This allows overriding defaults from libraries:

```openscad
// main.scad
include <lib.scad>
a = 2;
echo(b);  // 3

// lib.scad
a = 1;
b = a + 1;
```

### Special variables

Variables starting with $ are special (dynamic) and provide an alternate way to pass arguments to modules/functions.

## Vectors

A vector (list) is a sequence of zero or more values (numbers, booleans, strings, vectors, etc.).

Examples:

```openscad
[1, 2, 3]
[a, 5, b]
[]
[5.643]
["a", "b", "string"]
[[1, r], [x, y, z, 4, 5]]
[3, 5, [6, 7], [[8, 9], [10, [11, 12], 13], c, "string"]]
[4/3, 6*1.5, cos(60)]

// Usage:
cube([width, depth, height]);
translate([x, y, z])
polygon([[x0, y0], [x1, y1], [x2, y2]]);
```

### Creation

```openscad
cube([10, 15, 20]);

a1 = [1, 2, 3];
a2 = [4, 5];
a3 = [6, 7, 8, 9];
b  = [a1, a2, a3];  // [[1,2,3], [4,5], [6,7,8,9]]
```

Vector comprehensions:

```openscad
n = 10;
a = 0;
result = [ for (i = [0 : n-1]) a ];
echo(result);  // ECHO: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

n = 10;
a = 0;
b = 1;
result = [ for (i = [0 : n-1]) (i % 2 == 0) ? a : b ];
echo(result);  // ECHO: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
```

### Indexing elements within vectors

Elements are indexed from 0 to len(v)-1.

```openscad
e[5]            // element #5 at top level
e[5][2]         // element 2 of element 5
e[5][2][0]      // element 0 of the above
e[5][2][0][1]   // and so on
```

Example dataset:

```openscad
e = [ [1], [], [3,4,5], "string", "x", [[10,11],[12,13,14],[[15,16],[17]]] ];  // length 6
```

Address | len() | Element/Value
---|---:|---
e[0] | 1 | [1]
e[1] | 0 | []
e[5] | 3 | [[10,11], [12,13,14], [[15,16],[17]]]
e[5][1] | 3 | [12, 13, 14]
e[5][2] | 2 | [[15,16], [17]]
e[5][2][0] | 2 | [15, 16]
e[5][2][0][1] | undef | 16
e[3] | 6 | "string"
e[3][2] | 1 | "r"

Additional indexing expressions:

```openscad
s = [2, 0, 5];
a = 2;
```

Address | len() | Element/Value
---|---:|---
s[a] | undef | 5
e[s[a]] | 3 | [[10,11], [12,13,14], [[15,16],[17]]]

### String indexing

```openscad
"string"[2];  // "r"
```

### Dot notation indexing

The first three elements of a vector can be accessed with dot notation:

```openscad
e.x;  // e[0]
e.y;  // e[1]
e.z;  // e[2]
```

### Vector operators

#### concat

(Requires version 2015.03)

concat() flattens and joins vectors (no change in nesting level).

```openscad
vector1 = [1, 2, 3];
vector2 = [4];
vector3 = [5, 6];

new_vector = concat(vector1, vector2, vector3);  // [1,2,3,4,5,6]

string_vector = concat("abc", "def");            // ["abc", "def"]
one_string    = str(string_vector[0], string_vector[1]);  // "abcdef"
```

#### len

len() returns the length of a vector or string. Single non-vector values raise an error.

```openscad
a = [1, 2, 3];
echo(len(a));  // 3
```

### Matrix

A matrix is a vector of vectors.

```openscad
mr = [
  [ cos(angle), -sin(angle)],
  [ sin(angle),  cos(angle)]
];
```

## Objects (associative maps)

(Requires development snapshot)

Objects store collections of named values, analogous to JavaScript objects or Python dictionaries. Creation is currently not available in OpenSCAD; functions may return objects.

### Retrieving a value from an object

```openscad
obj.name     // for identifier-like names
obj["name"]  // for arbitrary string keys
```

### Iterating over object members

```openscad
for (name = obj) {
  // name is the member name
  value = obj[name];
  // ...
}
```

Works with flow-control for, intersection_for(), and list comprehensions.

## Getting input

There is no interactive input during script execution. Variables can be set via:
- Assignments in the script
- Customizer
- -D variable=value at the command line
- Limited file-based data access (e.g., dxf, stl, png)

### Getting a point from a drawing

dxf_cross reads the intersection of two lines (on a specified layer) and returns the point. The DXF must contain two lines that intersect (not point entities).

```openscad
OriginPoint = dxf_cross(
  file   = "drawing.dxf",
  layer  = "SCAD.Origin",
  origin = [0, 0],
  scale  = 1
);
```

### Getting a dimension value

dxf_dim reads a named dimension (using an identifier in the drawing instead of the numeric value).

```openscad
TotalWidth = dxf_dim(
  file   = "drawing.dxf",
  name   = "TotalWidth",
  layer  = "SCAD.Origin",
  origin = [0, 0],
  scale  = 1
);
```

---

# En.Wikibooks.Org Wiki Openscad User Manual Importing Geometry Import

# OpenSCAD User Manual: Importing Geometry

Importing is achieved by the import() command.
Note: Requires version 2015.03-2 or later for most features noted below.

The File → Open command may be used to insert an import() command. The file type filter may show only OpenSCAD files, but the file name can be replaced with a wildcard (e.g. *.stl) to browse additional file types.

## Supported file types

- 3D geometry formats
  - STL (ASCII and Binary)
  - OFF
  - OBJ
  - AMF (deprecated)
  - 3MF
- 2D geometry formats
  - DXF
  - PDF
  - SVG
- Data formats
  - JSON
  - CSV
    - Note: Treated as JSON input by import(); not the same as spreadsheet CSV.
- Other
  - CSG: import via include<> or loaded like an .scad file
  - PNG: import via surface()

## import

Imports a file for use in the current OpenSCAD model. The file extension determines the type.

### Parameters

- file
  - String path to file. If not absolute, it is resolved relative to the importing script.
  - Note: When using include<> with a script that calls import(), the path is resolved relative to the including script.
- center
  - Boolean. If true, places the center of the object at the origin.
  - Note: Development snapshot.
- convexity
  - Integer. Maximum number of front or back faces a ray may penetrate. Used only for correct OpenCSG preview and has no effect on final CGAL render.
- id
  - String. SVG import only; the element or group ID to import. Labels do not work here.
  - Note: Development snapshot.
- layer
  - String. DXF and SVG import only; layer name to import.
- $fn
  - Number. Segments used when converting circles/arcs/curves to polygons.
  - Note: Development snapshot.
- $fa
  - Number. Minimum angle step for polygon conversion of circles/arcs.
  - Note: Development snapshot.
- $fs
  - Number. Minimum segment length for polygon conversion of circles/arcs.
  - Note: Development snapshot.

### Examples

```openscad
import("example012.stl", convexity = 3);
```

```openscad
// Windows: escape backslashes or use forward slashes
import("D:/Documents and Settings/User/My Documents/Gear.stl", convexity = 3);
```

```openscad
// For data formats, the imported content is assigned to a variable
data = import("data.json");
```

Read a layer of a 2D DXF file and create a 3D shape:

```openscad
linear_extrude(height = 5, center = true, convexity = 10)
    import_dxf(file = "example009.dxf", layer = "plate");
```

## Convexity

Convexity is the maximum number of times a ray may intersect the front or back faces of the shape. For most models, setting convexity to 10 is sufficient for correct OpenCSG preview. It does not affect final CGAL rendering.

## Notes

In recent versions, import() is used for both 2D (e.g., DXF for extrusion) and 3D (e.g., STL) files.

## CGAL ERROR: assertion violation!

If you plan to render imported STL files, ensure the STL is “clean” (manifold, no holes, no self-intersections). A non-manifold STL may preview but fail on render with warnings or errors such as:

```
CGAL error in CGAL_Build_PolySet: CGAL ERROR: assertion violation!
Expr: check_protocoll == 0
File: .../include/CGAL/Polyhedron_incremental_builder_3.h
Line: 199
```

or

```
CGAL error in CGAL_Nef_polyhedron3(): CGAL ERROR: assertion violation!
Expr: pe_prev->is_border() || !internal::Plane_constructor<Plane>::get_plane(pe_prev->facet(),pe_prev->facet()->plane()).is_degenerate()
File: .../include/CGAL/Nef_3/polyhedron_3_to_nef_3.h
Line: 253
```

Ways to clean STL files:

- netfabb (repair holes; not self-intersections in some editions)
- MeshLab (can fix manifold issues and fill holes)
  - Render → Show non Manif Edges
  - Render → Show non Manif Vertices
  - Filters → Selection → Select non Manifold Edges (or Vertices), Apply, Close
  - Delete the selected vertices/edges
  - Use Fill Holes tool; repeat until all holes are filled
  - Export mesh as STL
- Blender (if MeshLab cannot fill the last hole)
  - Remove default object: X, 1
  - File → Import → STL
  - Enter Edit mode: Tab
  - Deselect all: A
  - Select non-manifold: Alt+Ctrl+Shift+M
  - Navigate: MMB to rotate, Shift+MMB to pan, wheel to zoom
  - Circle select: C (Esc to finish)
  - Merge vertices: Alt+M → At Center (or press Space and search “merge”)

Merging nearby vertices can be an effective way to close tiny gaps that are below typical 3D printer tolerances.

## Importing JSON

Requires enabling the import-function feature in a development build.

If you import a file with suffix .json or .csv, import() returns a JSON object datatype which cannot be expressed as a literal in OpenSCAD; it must be imported from a file. Note: .csv files are treated as JSON here and must contain JSON, not spreadsheet CSV.

Example input file contents:
```
{"people":[{"name":"Helen", "age":19}, {"name":"Chris", "age":32}]}
```

Example usage:
```openscad
/* people.json as shown above */
t = import("people.json");
echo(t);
people = t.people;

for (i = [0 : len(people) - 1]) {
    person = people[i];
    echo(str(person.name, ": ", person.age));
}
```

Result:
```
ECHO: { people = [{ age = 19; name = "Helen"; }, { age = 32; name = "Chris"; }]; }
ECHO: "Helen: 19"
ECHO: "Chris: 32"
```

## import_dxf (Deprecated)

Deprecated: import_dxf() will be removed in a future release. Use import() instead.

```openscad
// Read a DXF layer and extrude
linear_extrude(height = 5, center = true, convexity = 10)
    import_dxf(file = "example009.dxf", layer = "plate");
```

## import_stl (Deprecated)

Deprecated: import_stl() will be removed in a future release. Use import() instead.

```openscad
import_stl("body.stl", convexity = 5);
```

## surface

surface() reads heightmap information from text or image files. It can read PNG files.

### Parameters

- file
  - String. Path to the heightmap data file.
- center
  - Boolean. If true, center the object in X and Y; otherwise place in positive quadrant. Default: false.
- invert
  - Boolean. Inverts mapping of image color values to height values. No effect for text data files. Default: false.
  - Note: Requires version 2015.03.
- convexity
  - Integer. As with import(), affects OpenCSG preview only.

### Text file format

- A matrix of numbers representing heights.
- Rows map to Y-axis; columns map to X-axis.
- Numbers separated by spaces or tabs.
- Empty lines and lines starting with # are ignored.

### Images

Requires version 2015.03.

- Currently only PNG is supported.
- Alpha channel is ignored.
- Height is derived from grayscale using linear luminance for sRGB: Y = 0.2126 R + 0.7152 G + 0.0722 B.
- Grayscale values are scaled to range 0 to 100.

### Examples

Example 1:

```openscad
// surface.scad
surface(file = "surface.dat", center = true, convexity = 5);
%translate([0, 0, 5]) cube([10, 10, 10], center = true);
```

surface.dat:
```
10 9 8 7 6 5 5 5 5 5
9 8 7 6 6 4 3 2 1 0
8 7 6 6 4 3 2 1 0 0
7 6 6 4 3 2 1 0 0 0
6 6 4 3 2 1 1 0 0 0
6 6 3 2 1 1 1 0 0 0
6 6 2 1 1 1 1 0 0 0
6 6 1 0 0 0 0 0 0 0
3 1 0 0 0 0 0 0 0 0
3 0 0 0 0 0 0 0 0 0
```

Example 2:

```openscad
// example010.dat generated using octave:
// d = (sin(1:0.2:10)' * cos(1:0.2:10)) * 10;
// save("example010.dat", "d");
intersection() {
    surface(file = "example010.dat", center = true, convexity = 5);
    rotate(45, [0, 0, 1])
        surface(file = "example010.dat", center = true, convexity = 5);
}
```

Example 3 (Requires version 2015.03):

```openscad
// Example 3a
scale([1, 1, 0.1])
    surface(file = "smiley.png", center = true);

// Example 3b
scale([1, 1, 0.1])
    surface(file = "smiley.png", center = true, invert = true);
```

Example 3 demonstrates using surface() with a PNG image as a heightmap input.

---

# En.Wikibooks.Org Wiki Openscad User Manual Using The 2D Subsystem 3D To 2D Projection

# OpenSCAD User Manual — Using the 2D Subsystem

All 2D primitives can be transformed with 3D transformations. They are usually used as part of a 3D extrusion. Although 2D shapes are infinitely thin, they are rendered with a 1-unit thickness for preview.

Note: Subtracting 2D shapes from 3D objects with difference() can lead to unexpected results in preview; use proper 2D-to-3D extrusion first.

## 2D Primitives

### square

Creates a square or rectangle in the first quadrant. When center is true the square is centered on the origin.

Signatures:
- square(size = [x, y], center = true/false);
- square(size = x, center = true/false);

Parameters:
- size:
  - single value: a square with both sides this length
  - 2-value array [x, y]: a rectangle with dimensions x and y
- center:
  - false (default): 1st (positive) quadrant, one corner at (0, 0)
  - true: shape is centered at (0, 0)

Defaults:
- square(); yields: square(size = [1, 1], center = false);

Examples (equivalent scripts):

```openscad
// Square 10×10
square(size = 10);
square(10);
square([10, 10]);

// Centered control
square(10, false);
square([10, 10], false);
square([10, 10], center = false);
square(size = [10, 10], center = false);
square(center = false, size = [10, 10]);

// Rectangle 20×10, centered
square([20, 10], true);
a = [20, 10];
square(a, true);
```

### circle

Creates a circle at the origin. All parameters, except r, must be named.

Signature:
- circle(r = radius | d = diameter);

Parameters:
- r: circle radius. This is the only optional named parameter (you may call circle(10)).
- d: circle diameter.
- $fa: minimum angle (in degrees) of each fragment.
- $fs: minimum circumferential length of each fragment.
- $fn: fixed number of fragments in 360 degrees. Values of 3 or more override $fa and $fs.

Notes:
- Circle resolution is based on size, using $fa or $fs. For small, high-resolution circles, either scale down a larger circle or set $fn.

Examples:

```openscad
// High-resolution small circle
scale([1/100, 1/100, 1/100]) circle(200);  // radius 2 at high resolution

// Another way
circle(2, $fn = 50);
```

Defaults:
- circle(); yields: circle($fn = 0, $fa = 12, $fs = 2, r = 1);

Equivalent scripts:

```openscad
circle(10);
circle(r = 10);
circle(d = 20);
circle(d = 2 + 9*2);
```

#### Ellipses

Create an ellipse from a circle using scale() or resize() to make x and y unequal.

```openscad
resize([30, 10]) circle(d = 20);
scale([1.5, 0.5]) circle(d = 20);
```

#### Regular Polygons

A regular polygon of 3 or more sides can be created by using circle() with $fn set to the number of sides.

```openscad
// Square via circle with 4 fragments
circle(r = 1, $fn = 4);

module regular_polygon(order = 4, r = 1) {
  angles = [for (i = [0:order-1]) i*(360/order)];
  coords = [for (th = angles) [r*cos(th), r*sin(th)]];
  polygon(coords);
}
regular_polygon();
```

Example script producing several polygons:

```openscad
translate([-42,  0]) { circle(20, $fn = 3); %circle(20, $fn = 90); }
translate([  0,  0])  circle(20, $fn = 4);
translate([ 42,  0])  circle(20, $fn = 5);
translate([-42, -42]) circle(20, $fn = 6);
translate([  0, -42]) circle(20, $fn = 8);
translate([ 42, -42]) circle(20, $fn = 12);

color("black") {
  translate([-42,   0, 1]) text("3",  7, , center);
  translate([  0,   0, 1]) text("4",  7, , center);
  translate([ 42,   0, 1]) text("5",  7, , center);
  translate([-42, -42, 1]) text("6",  7, , center);
  translate([  0, -42, 1]) text("8",  7, , center);
  translate([ 42, -42, 1]) text("12", 7, , center);
}
```

### polygon

Creates a multi-sided 2D shape from a list of x, y coordinates. Supports concave/convex edges and holes.

Signature:
- polygon(points = [[x, y], ...], paths = [[p1, p2, ...], ...], convexity = N);

Parameters:
- points: list of [x, y] point coordinates (indices 0..n-1).
- paths:
  - default: if omitted, all points are used in listed order.
  - single vector: order of point indices; can re-order and use a subset.
  - multiple vectors: first is the outer boundary; subsequent paths are holes, subtracted from the primary shape.
  - Each path closes automatically from last point back to the first.
- convexity: integer maximum number of front/back face crossings a ray might intersect (affects OpenCSG preview only).

Defaults:
- polygon(); yields: polygon(points = undef, paths = undef, convexity = 1);

#### Without holes

```openscad
polygon(points = [[0,0], [100,0], [130,50], [30,50]]);
polygon([[0,0], [100,0], [130,50], [30,50]], paths = [[0,1,2,3]]);
polygon([[0,0], [100,0], [130,50], [30,50]], [[3,2,1,0]]);
polygon([[0,0], [100,0], [130,50], [30,50]], [[1,0,3,2]]);

a = [[0,0], [100,0], [130,50], [30,50]];
b = [[3,0,1,2]];
polygon(a);
polygon(a, b);
polygon(a, [[2,3,0,1,2]]);
```

#### One hole

```openscad
polygon(
  points = [[0,0], [100,0], [0,100], [10,10], [80,10], [10,80]],
  paths  = [[0,1,2], [3,4,5]],
  convexity = 10
);

triangle_points = [[0,0], [100,0], [0,100], [10,10], [80,10], [10,80]];
triangle_paths  = [[0,1,2], [3,4,5]];
polygon(triangle_points, triangle_paths, 10);
```

The first path [0,1,2] defines the outer boundary; the second [3,4,5] defines the hole and is subtracted.

#### Multi hole

Note: Requires version 2015.03 (for concat()).

```openscad
// Example polygon with multiple holes
a0 = [[0,0], [100,0], [130,50], [30,50]];        // main
b0 = [1,0,3,2];

a1 = [[20,20], [40,20], [30,30]];                // hole 1
b1 = [4,5,6];

a2 = [[50,20], [60,20], [40,30]];                // hole 2
b2 = [7,8,9];

a3 = [[65,10], [80,10], [80,40], [65,40]];       // hole 3
b3 = [10,11,12,13];

a4 = [[98,10], [115,40], [85,40], [85,10]];      // hole 4
b4 = [14,15,16,17];

a = concat(a0, a1, a2, a3, a4);
b = [b0, b1, b2, b3, b4];

polygon(a, b);
// Alternate
polygon(a, [b0, b1, b2, b3, b4]);
```

#### Extruding a 3D shape from a polygon

```openscad
translate([0, -20, 10]) {
  rotate([90, 180, 90]) {
    linear_extrude(50) {
      polygon(points = [
        // x,y
        /* O . */               [-2.8, 0],
        /* O__X . */            [-7.8, 0],
        /* O \ X__X . */        [-15.3633, 10.30],
        /* X_______._____O \ X__X . */ [15.3633, 10.30],
        /* X_______._______X \ / X__X . O */ [7.8, 0],
        /* X_______._______X \ / X__X . O__X */ [2.8, 0],
        /* X__________.__________X \ / \ O / \ / / \ / / X__X . X__X */ [5.48858, 5.3],
        /* X__________.__________X \ / \ O__________X / \ / / \ / / X__X . X__X */ [-5.48858, 5.3],
      ]);
    }
  }
}
```

#### convexity (preview hint)

The convexity parameter specifies the maximum number of front/back faces a ray might intersect. It only affects OpenCSG preview and not final CGAL mesh generation. A value around 10 generally works well.

### import_dxf (deprecated)

Deprecated: import_dxf() is deprecated and will be removed in a future release. Use import() instead.

```openscad
linear_extrude(height = 5, center = true, convexity = 10)
  import_dxf(file = "example009.dxf", layer = "plate");
```

## Text

The text() module creates text as a 2D object using fonts installed on the local system or provided as separate font files.

Parameters:
- text: string to render.
- size: approximate ascent (height above baseline). Default 10. Approx. points: pt = size / 3.937.
- font: logical font name; may include style, e.g., "Liberation Sans:style=Bold Italic".
- halign: "left" (default), "center", "right".
- valign: "top", "center", "baseline" (default), "bottom".
- spacing: character spacing factor (default 1).
- direction: "ltr" (default), "rtl", "ttb", "btt".
- language: language tag, e.g., "en" (default).
- script: script tag, e.g., "latin" (default).
- $fn: used for subdividing curved path segments.

Example 1:

```openscad
text("OpenSCAD");
```

Notes:
- Unicode escapes:
  - \x03  — hex char value (01–7f)
  - \u0123 — 4-hex-digit Unicode (lowercase \u)
  - \U012345 — 6-hex-digit Unicode (uppercase \U)
- The null character (NUL) maps to space (SP).

```openscad
assert(version() == [2019, 5, 0]);
assert(ord(" ") == 32);
assert(ord("\x00") == 32);
assert(ord("\u0000") == 32);
assert(ord("\U000000") == 32);

t = "\u20AC10 \u263A";  // "€10 ☺"
```

### Using Fonts & Styles

Fonts are specified by logical name; styles can be appended, e.g.:

```openscad
text("Styled", font = "Liberation Sans:style=Bold Italic");
```

Add project-specific font files (TrueType .ttf, OpenType .otf) with use<>:

```openscad
use <ttf/paratype-serif/PTF55F.ttf>
```

List system fonts (examples):

```
fc-list -f "%-60{{%{family[0]}%{:style[0]=}}}%{file}\n" | sort
```

On Windows, list fonts from the registry:

```
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" /s > List_Fonts_Windows.txt
```

Example 2:

```openscad
square(10);

translate([15, 15]) {
  text("OpenSCAD", font = "Liberation Sans");
}

translate([15, 0]) {
  text("OpenSCAD", font = "Liberation Sans:style=Bold Italic");
}
```

### Alignment

#### Vertical alignment

- top: top of tallest glyph at Y
- center: vertical center of the text’s bounding box at Y
- baseline: font baseline at Y (default)
- bottom: bottom of lowest descender at Y

```openscad
text = "Align";
font = "Liberation Sans";
valign = [
  [  0, "top"],
  [ 40, "center"],
  [ 75, "baseline"],
  [110, "bottom"]
];

for (a = valign) {
  translate([10, 120 - a[0], 0]) {
    color("red")  cube([135, 1, 0.1]);
    color("blue") cube([1, 20, 0.1]);
    linear_extrude(height = 0.5) {
      text(text = str(text, "_", a[1]), font = font, size = 20, valign = a[1]);
    }
  }
}
```

Multi-line text is not directly supported; render each line with translate(). Use valign = "baseline" and about 1.6*size line spacing for typical single-spacing.

#### Horizontal alignment

- left (default): left of bounding box at X
- center: center of bounding box at X
- right: right of bounding box at X

```openscad
text = "Align";
font = "Liberation Sans";
halign = [
  [10, "left"],
  [50, "center"],
  [90, "right"]
];

for (a = halign) {
  translate([140, a[0], 0]) {
    color("red")  cube([115, 2, 0.1]);
    color("blue") cube([2, 20, 0.1]);
    linear_extrude(height = 0.5) {
      text(text = str(text, "_", a[1]), font = font, size = 20, halign = a[1]);
    }
  }
}
```

### 3D text

Convert 2D text to 3D using linear_extrude:

```openscad
// 3D Text Example
linear_extrude(4)
  text("Text");
```

### Metrics

Note: Requires development snapshot for some metric functions.

#### textmetrics()

Returns metrics for how text() would render.

Members:
- position: lower-left corner of generated text
- size: width/height of generated text
- ascent: above baseline
- descent: below baseline
- offset: lower-left including any pre-glyph spacing
- advance: point at which additional text should be positioned

```openscad
s = "Hello, World!";
size = 20;
font = "Liberation Serif";

tm = textmetrics(s, size = size, font = font);
echo(tm);

translate([0, 0, 1]) text("Hello, World!", size = size, font = font);
color("black") translate(tm.position) square(tm.size);
```

Example echo (reformatted):

```
ECHO: {
  position = [0.7936, -4.2752];
  size     = [149.306, 23.552];
  ascent   = 19.2768;
  descent  = -4.2752;
  offset   = [0, 0];
  advance  = [153.09, 0];
}
```

#### fontmetrics()

Returns global font characteristics.

Parameters:
- size: optional; as for text()
- font: optional; as for text()

Returns object:
- nominal: ascent, descent (typical glyph)
- max: ascent, descent (maximum)
- interline: baseline-to-baseline spacing
- font: family, style

```openscad
echo(fontmetrics(font = "Liberation Serif"));
```

Example echo (reformatted):

```
ECHO: {
  nominal = { ascent = 12.3766; descent = -3.0043; };
  max     = { ascent = 13.6312; descent = -4.2114; };
  interline = 15.9709;
  font = { family = "Liberation Serif"; style = "Regular"; };
}
```

## 3D to 2D Projection

Using projection(), you can create 2D drawings from 3D models, and export them to DXF. It projects a 3D model to the (x, y) plane at z = 0.

- cut = true: only points with z = 0 are considered (slice)
- cut = false (default): points above and below the plane contribute (shadow-like projection)

Examples:

```openscad
// Cut projection: slice at z=0
projection(cut = true)
  example002();
```

```openscad
// Ordinary projection: shadow onto XY
projection(cut = false)
  example002();
```

Side-view projection:

```openscad
// Move and orient out of XY plane
translate([0, 0, 25])
  rotate([90, 0, 0])
  example002();

// Project side view
projection()
  translate([0, 0, 25])
  rotate([90, 0, 0])
  example002();
```

## 2D to 3D Extrusion

Extrusion creates a 3D object from a 2D cross-section. OpenSCAD provides:
- linear_extrude()
- rotate_extrude()

Extrusions operate on the 2D shape’s projection onto the XY plane. Any prior Z transforms on 2D shapes are ignored during extrusion.

### linear_extrude

Linear extrusion moves the 2D shape along a vector V (default +Z). The shape can be twisted and scaled along the height.

Usage:

```openscad
linear_extrude(
  height   = 5,
  v        = [0, 0, 1],   // Requires > 2021.01 for custom vectors
  center   = true,
  convexity= 10,
  twist    = -fanrot,
  slices   = 20,
  scale    = 1.0,
  $fn      = 16
) {
  // 2D child
}
```

Notes:
- Use named parameters.
- height must be positive.
- $fn sets resolution of the extrusion spine; higher is smoother.
- If extrusion fails for complex shapes, increase convexity (e.g., 10).

#### Twist

Twist is degrees the shape rotates while extruding. twist = 360 turns one full revolution. Direction follows left-hand rule.

```openscad
// 0° twist
linear_extrude(height = 10, center = true, convexity = 10, twist = 0)
  translate([2, 0, 0]) circle(r = 1);

// -100°
linear_extrude(height = 10, center = true, convexity = 10, twist = -100)
  translate([2, 0, 0]) circle(r = 1);

// +100°
linear_extrude(height = 10, center = true, convexity = 10, twist = 100)
  translate([2, 0, 0]) circle(r = 1);

// -500°
linear_extrude(height = 10, center = true, convexity = 10, twist = -500)
  translate([2, 0, 0]) circle(r = 1);
```

#### Center

If center is false, Z range is [0, height]. If true, range is [-height/2, height/2].

```openscad
// center = true
linear_extrude(height = 10, center = true, convexity = 10, twist = -500)
  translate([2, 0, 0]) circle(r = 1);

// center = false
linear_extrude(height = 10, center = false, convexity = 10, twist = -500)
  translate([2, 0, 0]) circle(r = 1);
```

#### Mesh Refinement

- slices: number of intermediate layers along Z. Defaults increase with twist.
- segments: adds vertices on the 2D polygon’s edges to smooth twisted geometry. Must be a multiple of the polygon’s fragment count (e.g., 6 or 9 for circle($fn=3), 8 or 12 for square()).
- $fn, $fs, $fa also affect smoothness. If slices is not set, it may derive from $fn.

```openscad
linear_extrude(height = 10, center = false, convexity = 10, twist = 360, slices = 100)
  translate([2, 0, 0]) circle(r = 1);
```

```openscad
linear_extrude(height = 10, center = false, convexity = 10, twist = 360, $fn = 100)
  translate([2, 0, 0]) circle(r = 1);
```

#### Scale

Scale the 2D shape over the extrusion height. Can be scalar or vector.

```openscad
// Uniform scale
linear_extrude(height = 10, center = true, convexity = 10, scale = 3)
  translate([2, 0, 0]) circle(r = 1);

// Non-uniform scale
linear_extrude(height = 10, center = true, convexity = 10, scale = [1, 5], $fn = 100)
  translate([2, 0, 0]) circle(r = 1);
```

Note: Vector scale plus twist may produce nonplanar side walls. Use twist = 0 and set slices to avoid asymmetry.

```openscad
linear_extrude(height = 10, scale = [1, 0.1], slices = 20, twist = 0)
  polygon(points = [[0,0], [20,10], [20,-10]]);
```

#### Using with imported SVG

```openscad
linear_extrude(height = 10, center = true)
  import("knight.svg");
```

### rotate_extrude

Rotational extrusion spins a 2D shape around the Z axis to form a rotationally symmetric 3D solid. The 2D shape must lie entirely on one side of the Y axis (x >= 0 recommended). If the shape touches x = 0, it must be along a line, not a point.

Notes:
- Operates on the shape’s projection onto the XY plane.
- translate in X changes resulting diameter; translate in Y shifts result in Z.
- rotate about X or Y distorts the cross-section via the projection.
- Cannot produce a helix or screw thread directly.
- In older versions, shapes on x < 0 could have inverted faces.

Usage:

```openscad
rotate_extrude(angle = 360, start = 0, convexity = 2) {
  // 2D child
}
```

Parameters:
- Use named parameters (pre-2021.01).
- convexity: increase if preview fails (e.g., 10).
- angle (>= 2019.05): sweep degrees; negative sweeps clockwise (right-hand rule).
- start (dev snapshots): starting angle counter-clockwise from +X.
- $fa, $fs, $fn as usual.

Examples:

```openscad
// Simple torus-like shape
rotate_extrude(convexity = 10)
  translate([2, 0, 0]) circle(r = 1);
```

Mesh refinement:

```openscad
// Increase 2D shape fragments
rotate_extrude(convexity = 10)
  translate([2, 0, 0]) circle(r = 1, $fn = 100);

// Increase extrusion fragments, too
rotate_extrude(convexity = 10, $fn = 100)
  translate([2, 0, 0]) circle(r = 1, $fn = 100);
```

Hook using angle:

```openscad
eps = 0.01;

translate([eps, 60, 0])
  rotate_extrude(angle = 270, convexity = 10)
  translate([40, 0]) circle(10);

rotate_extrude(angle = 90, convexity = 10)
  translate([20, 0]) circle(10);

translate([20, eps, 0])
  rotate([90, 0, 0]) cylinder(r = 10, h = 80 + eps);
```

Extruding a polygon:

```openscad
// 2D polygon (shown rotated to view cross-section)
rotate([90, 0, 0])
  polygon(points = [[0,0], [2,1], [1,2], [1,3], [3,4], [0,5]]);

// Rotational extrusion
rotate_extrude($fn = 200)
  polygon(points = [[0,0], [2,1], [1,2], [1,3], [3,4], [0,5]]);
```

#### Orientation

- With angle not specified (full 360 in older versions), the extrusion traditionally starts along the negative X axis.
- With angle specified and not 360, starts at the positive X axis.
- Some version differences exist for angle = 360; specifying angle = 360 yields consistent behavior starting at +X in recent development snapshots.
- start (dev snapshots) directly controls start angle.

### Description of extrude parameters

#### For all extrusion modes

- convexity: integer. Max number of front/back intersections for a ray. Only affects OpenCSG preview; not mesh generation. Higher values may slow preview.

#### For linear extrusion only

- height: extrusion height
- center: center the solid around the mid-plane if true
- twist: degrees of rotation along height
- scale: scale factor (scalar or [sx, sy]) across height
- slices: like $fn for the extrusion spine; not passed to child shape
- segments: adds points along polygon segments for smoother twisted results

## DXF Extrusion

Using import() with extrusion to convert 2D DXF into 3D.

### Linear Extrude

```openscad
linear_extrude(height = fanwidth, center = true, convexity = 10)
  import(file = "example009.dxf", layer = "fan_top");
```

### Rotate Extrude

```openscad
rotate_extrude(convexity = 10)
  import(file = "example009.dxf", layer = "fan_side", origin = fan_side_center);
```

### Getting Inkscape to work

Inkscape (an open-source drawing program) can produce 2D DXF suitable for OpenSCAD. Use DXF export methods that preserve paths and curves as needed for your workflow.

---

# En.Wikibooks.Org Wiki Openscad User Manual Transformations Color

# OpenSCAD User Manual — Transformations

## Basic concept

Transformations affect their child nodes by moving, rotating, or scaling them. Transformations are written before the object they affect.

Example:
```openscad
translate([10,20,30]) cube(10);
```

There is no semicolon after the transformation.

Apply to a group of child nodes by enclosing them in braces:
```openscad
translate([0,0,-5]) {
  cube(10);
  cylinder(r=5, h=10);
}
```

Cascading transformations are achieved by nesting:
```openscad
rotate([45,45,45])
translate([10,20,30])
cube(10);
```

When combining transforms, order is important. Transformations are applied from right to left.

```openscad
// Rotates around origin, then moves, then colors red
color("red")
translate([0,10,0])
rotate([45,0,0])
cube(5);

// Moves first, then rotates around origin, then colors green
color("green")
rotate([45,0,0])
translate([0,10,0])
cube(5);
```

## Advanced concept

In preview (F5), traditional transforms (translate, rotate, scale, mirror, multmatrix) are performed using OpenGL, while others (e.g., resize) perform a CGAL operation, behaving like a CSG operation that affects the underlying geometry. This can impact modifier characters (“#” highlight and “%” disable), which may apply to pre- vs. post-transformed geometry depending on the operation.

## scale

Scales child elements multiplicatively by the specified vector.

Usage:
```openscad
scale(v = [x, y, z]) { /* children */ }
```

Example:
```openscad
cube(10);
translate([15,0,0])
scale([0.5, 1, 2])
cube(10);
```

## resize

Modifies the size of the child object to match the given x, y, and z sizes. This is a CGAL operation and can be slower, even in preview.

Usage:
```openscad
// resize the sphere to extend 30 in x, 60 in y, and 10 in z
resize(newsize = [30,60,10]) sphere(r=10);

// if x, y, or z is 0, that dimension is left as-is
resize([2,2,0]) cube();

// auto scales 0-dimensions to match
// resize the 1x2x0.5 cube to 7x14x3.5
resize([7,0,0], auto=true) cube([1,2,0.5]);

// auto for specific dimensions only
// resize to 10x8x1; z dimension left alone
resize([10,0,0], auto=[true,true,false]) cube([5,4,1]);
```

## rotate

Rotates its child by ‘a’ degrees about an axis of the coordinate system or around an arbitrary axis.

Usage:
```openscad
// About arbitrary axis v
rotate(a = deg_a, v = [x, y, z]) { /* children */ }
// or
rotate(deg_a, [x, y, z]) { /* children */ }

// Euler-like per-axis rotation (order x then y then z)
rotate(a = [deg_x, deg_y, deg_z]) { /* children */ }
// or
rotate([deg_x, deg_y, deg_z]) { /* children */ }
```

When ‘a’ is an array, ‘v’ is ignored. Per-axis rotations apply in order x, then y, then z:
```openscad
// Equivalent expansions
rotate(a=[ax,ay,az]) {...}

// is equivalent to:
rotate([0,0,az])
rotate([0,ay,0])
rotate([ax,0,0]) {...}
```

Examples:
```openscad
// Flip upside-down around Y
rotate([0,180,0]) { /* children */ }

// Equivalent single-axis form
rotate(a=180, v=[0,1,0]) { /* children */ }

// Rotate 45° around arbitrary axis [1,1,0]
rotate(a=45, v=[1,1,0]) { /* children */ }

// 2D convenience (around Z)
rotate(45) square(10);
```

### Rotation rule help

Right-hand rule:

- For rotate([a, b, c]):
  - a: rotation about X, from +Y toward +Z
  - b: rotation about Y, from +Z toward +X
  - c: rotation about Z, from +X toward +Y

Construct a cylinder from origin to point (x, y, z) using spherical coordinates:
```openscad
x = 10;
y = 10;
z = 10;               // endpoint
length = norm([x,y,z]);    // radial distance
b = acos(z/length);   // inclination
c = atan2(y,x);       // azimuth

rotate([0, b, c])
cylinder(h=length, r=0.5);

%cube([x,y,z]);       // cube corner coincides with cylinder end
```

## translate

Translates (moves) child elements by the specified vector.

Usage:
```openscad
translate(v = [x, y, z]) { /* children */ }
```

Example:
```openscad
cube(2, center=true);
translate([5,0,0]) sphere(1, center=true);
```

## mirror

Transforms the child element as a mirror image through a plane intersecting the origin. The argument is the normal vector of the mirror plane.

Function signature:
```openscad
mirror(v = [x, y, z]) { /* children */ }
```

Examples:
```openscad
// Original and mirrored hands (mirror changes the object; it does not duplicate)
hand();                  // original
mirror([1,0,0]) hand();

hand();                  // original
mirror([1,1,0]) hand();

hand();                  // original
mirror([1,1,1]) hand();
```

Mirroring a composite shape:
```openscad
// original
rotate([0,0,-30]) {
  cube([23,12,10]);
  translate([0.5, 4.4, 9.9]) {
    color("red", 1.0) {
      linear_extrude(height=2) {
        text("OpenSCAD", size=3);
      }
    }
  }
}

// mirrored
mirror([1,0,0]) {
  rotate([0,0,-30]) {
    cube([23,12,10]);
    translate([0.5, 4.4, 9.9]) {
      color("red", 1.0) {
        linear_extrude(height=2) {
          text("OpenSCAD", size=3);
        }
      }
    }
  }
}
```

## multmatrix

Multiplies the geometry of child elements by a 4×3 or 4×4 affine transformation matrix. The implicit 4th row is [0,0,0,1] if omitted.

Usage:
```openscad
multmatrix(m = [
  [m11, m12, m13, tx],
  [m21, m22, m23, ty],
  [m31, m32, m33, tz],
  [  0,   0,   0,  1]  // optional in OpenSCAD
]) {
  /* children */
}
```

The upper-left 3×3 handles scale, rotation, and shear; the last column is translation. Each vertex v=[x,y,z,1] is transformed as m*v.

Example: rotate 45° in XY, then translate [10,20,30] (equivalent to translate([10,20,30]) rotate([0,0,45])):
```openscad
angle = 45;
multmatrix(m = [
  [cos(angle), -sin(angle), 0, 10],
  [sin(angle),  cos(angle), 0, 20],
  [0,           0,          1, 30],
  [0,           0,          0,  1]
])
union() {
  cylinder(r=10, h=10, center=false);
  cube([10,10,10], center=false);
}
```

Combining matrices (equivalent to rotate([0, -35, 0]) translate([40, 0, 0]) Obj();):
```openscad
module Obj() {
  cylinder(r=10, h=10, center=false);
  cube([10,10,10], center=false);
}

// iterate into the future 6 times and show how multmatrix moves around the center point
for (time = [0 : 15 : 90]) {
  y_ang = -time;

  mrot_y = [
    [ cos(y_ang), 0, sin(y_ang), 0],
    [ 0,          1, 0,          0],
    [-sin(y_ang), 0, cos(y_ang), 0],
    [ 0,          0, 0,          1]
  ];

  mtrans_x = [
    [1, 0, 0, 40],
    [0, 1, 0,  0],
    [0, 0, 1,  0],
    [0, 0, 0,  1]
  ];

  echo(mrot_y * mtrans_x);

  // at origin
  Obj();

  // starting object at [40,0,0]
  multmatrix(mtrans_x) Obj();

  // rotated instance, appears 6 times
  multmatrix(mrot_y * mtrans_x) Obj();
}
```

Skew example (shear Z into Y):
```openscad
M = [
  [1, 0,   0, 0],
  [0, 1, 0.7, 0],  // skew value along y as z changes
  [0, 0,   1, 0],
  [0, 0,   0, 1]
];

multmatrix(M) {
  union() {
    cylinder(r=10, h=10, center=false);
    cube([10,10,10], center=false);
  }
}
```

Transforming a vector via matrix, then using it as a translation:
```openscad
angle = 45;
m = [
  [cos(angle), -sin(angle), 0, 0],
  [sin(angle),  cos(angle), 0, 0],
  [0,           0,          1, 0]
];

v = [10,0,0];
vm = concat(v, [1]);   // make it [x,y,z,1]
vtrans = m * vm;       // transformed vector

echo(vtrans);
translate(vtrans) cube();
```

## color

Displays children with the specified RGB color and optional alpha. Used in F5 preview; CGAL/STL (F6) do not support color. Alpha defaults to 1.0 (opaque).

Function signature:
```openscad
color(c = [r, g, b, a]) { /* children */ }
color(c = [r, g, b], alpha = 1.0) { /* children */ }
color("#hexvalue") { /* children */ }
color("colorname", 1.0) { /* children */ }
```

Notes:
- r, g, b, a are in [0,1]. For 0–255 sources, scale:
```openscad
color([R/255, G/255, B/255]) { /* children */ }
```
- Colors can be specified by name (case insensitive), e.g.:
```openscad
color("red") sphere(5);
color("Blue", 0.5) cube(5);
```
- Hex formats: #rgb, #rgba, #rrggbb, #rrggbbaa. If both hex alpha and alpha parameter are given, the parameter wins.
- Transparency is order-sensitive; list transparent objects after opaque ones for correct display. Some combinations of multiple transparent objects cannot be handled correctly.

Color name categories (subset from SVG color list):
- Purples: Lavender, Thistle, Plum, Violet, Orchid, Fuchsia, Magenta, MediumOrchid, MediumPurple, BlueViolet, DarkViolet, DarkOrchid, DarkMagenta, Purple, Indigo, DarkSlateBlue, SlateBlue, MediumSlateBlue
- Reds: IndianRed, LightCoral, Salmon, DarkSalmon, LightSalmon, Red, Crimson, FireBrick, DarkRed
- Blues: Aqua, Cyan, LightCyan, PaleTurquoise, Aquamarine, Turquoise, MediumTurquoise, DarkTurquoise, CadetBlue, SteelBlue, LightSteelBlue, PowderBlue, LightBlue, SkyBlue, LightSkyBlue, DeepSkyBlue, DodgerBlue, CornflowerBlue, RoyalBlue, Blue, MediumBlue, DarkBlue, Navy, MidnightBlue
- Pinks: Pink, LightPink, HotPink, DeepPink, MediumVioletRed, PaleVioletRed
- Greens: GreenYellow, Chartreuse, LawnGreen, Lime, LimeGreen, PaleGreen, LightGreen, MediumSpringGreen, SpringGreen, MediumSeaGreen, SeaGreen, ForestGreen, Green, DarkGreen, YellowGreen, OliveDrab, Olive, DarkOliveGreen, MediumAquamarine, DarkSeaGreen, LightSeaGreen, DarkCyan, Teal
- Oranges: LightSalmon, Coral, Tomato, OrangeRed, DarkOrange, Orange
- Yellows: Gold, Yellow, LightYellow, LemonChiffon, LightGoldenrodYellow, PapayaWhip, Moccasin, PeachPuff, PaleGoldenrod, Khaki, DarkKhaki
- Browns: Cornsilk, BlanchedAlmond, Bisque, NavajoWhite, Wheat, BurlyWood, Tan, RosyBrown, SandyBrown, Goldenrod, DarkGoldenrod, Peru, Chocolate, SaddleBrown, Sienna, Brown, Maroon
- Whites: White, Snow, Honeydew, MintCream, Azure, AliceBlue, GhostWhite, WhiteSmoke, Seashell, Beige, OldLace, FloralWhite, Ivory, AntiqueWhite, Linen, LavenderBlush, MistyRose
- Grays: Gainsboro, LightGrey, Silver, DarkGray, Gray, DimGray, LightSlateGray, SlateGray, DarkSlateGray, Black

Example: 3‑D multicolor sine wave
```openscad
for (i = [0:36]) {
  for (j = [0:36]) {
    color([ 0.5 + sin(10*i)/2,
            0.5 + sin(10*j)/2,
            0.5 + sin(10*(i+j))/2 ])
    translate([i, j, 0])
    cube(size = [1, 1, 11 + 10*cos(10*i)*sin(10*j)]);
  }
}
```
Since −1 ≤ sin(x) ≤ 1, each component 0.5 + sin(x)/2 remains within [0,1].

Example 2: Optional coloring via parameter
```openscad
module myModule(withColors=false) {
  c = withColors ? "red" : undef;
  color(c) circle(r=10);
}
```
Setting the color name to undef preserves default colors.

## offset

Note: Requires version 2015.03.

Default with no arguments: r = 1, chamfer = false. If both r and delta are given, r takes precedence.

Offset generates a new 2D outline from an existing outline. Two modes:
- Radial (r): rounded corners by sweeping a circle of radius r outside (r > 0) or inside (r < 0) the outline.
- Delta (delta): fixed-distance offset outside (delta > 0) or inside (delta < 0) with straight/angled corners. No inward perimeter is generated where it would self-intersect.

Use cases:
- Thin walls by subtracting a negative offset from the original (or vice versa).
- Fillet (round inside corners):
  - offset(r = -3) offset(delta = +3)
- Round (round outside corners):
  - offset(r = +3) offset(delta = -3)

Parameters:
| Name         | Type              | Description |
|--------------|-------------------|-------------|
| r            | Number            | Radius for radial mode (rounded corners). If unnamed first parameter, treated as r. Takes precedence over delta when both given. |
| delta        | Number            | Distance for delta mode (straight/angled corners). Negative values offset inward. |
| chamfer      | Boolean (false)   | Only for delta mode. If true, edges are chamfered (cut straight); otherwise edges extend to their intersection. |
| $fa, $fs, $fn| Special variables | Control curve smoothness for radial offsets. No effect on delta offsets. |

Examples:
```openscad
// Example 1
linear_extrude(height=60, twist=90, slices=60) {
  difference() {
    offset(r=10)  square(20, center=true);
    offset(r=8)   square(20, center=true);
  }
}

// Example 2: fillet helper
module fillet(r) {
  offset(r = -r) offset(delta = r) children();
}
```

## fill

Note: Requires development snapshot.

Fill removes holes from polygons without changing the outer outline. For convex polygons the result is identical to hull().

Example:
```openscad
t = "OpenSCAD";

linear_extrude(15) {
  text(t, 50);
}

color("darkslategray") {
  linear_extrude(2) {
    offset(4) {
      fill() {
        text(t, 50);
      }
    }
  }
}
```

## minkowski

Displays the Minkowski sum of child nodes.

Rounded-edge plate example:
```openscad
$fn = 50;
cube([10,10,1]);
cylinder(r=2, h=1);

$fn = 50;
minkowski() {
  cube([10,10,1]);
  cylinder(r=2, h=1);
}
```

Note: The origin of the second object affects the result.

Different sums due to centering:
```openscad
minkowski() {
  cube([10, 10, 1]);
  cylinder(1, center=true);
}

minkowski() {
  cube([10, 10, 1]);
  cylinder(1);
}
```

Warnings:
- Complexity grows multiplicatively with facet counts. High $fn can consume significant CPU and memory.
- If an input is compound (multiple separate shapes), it may be treated as multiple inputs and produce an oversized result. Use union() to combine before minkowski if needed.

## hull

Displays the convex hull of child nodes.

2D example:
```openscad
hull() {
  translate([15,10,0]) circle(10);
  circle(10);
}
```

Tip: For 3D-looking results like the hull of two cylinders, it can be more efficient to hull() their 2D circular bases and then linear_extrude, rather than hull() the 3D cylinders directly.

---

# En.Wikibooks.Org Wiki Openscad User Manual String Functions Chr

# OpenSCAD User Manual: String Functions

## str
Convert all arguments to strings and concatenate.

Usage examples:
```openscad
number = 2;
echo("This is ", number, 3, " and that's it.");
echo(str("This is ", number, 3, " and that's it."));

// Results:
// ECHO: "This is ", 2, 3, " and that's it."
// ECHO: "This is 23 and that's it."
```

Simple conversion of a number to a string:
```openscad
s = str(n);
```

## chr
[Note: Requires version 2015.03]

Convert numbers to a string containing the character with the corresponding code point.

- OpenSCAD uses Unicode; numbers are interpreted as Unicode code points.
- Numbers outside the valid code point range produce an empty string.

Parameters:
- chr(Number) — Convert one code point to a string of length 1 (byte length depends on UTF-8 encoding) if valid.
- chr(Vector) — Convert all code points in the vector to a string.
- chr(Range) — Convert all code points produced by the range to a string.

Examples:
```openscad
echo(chr(65), chr(97));              // ECHO: "A", "a"
echo(chr(65, 97));                   // ECHO: "Aa"
echo(chr([66, 98]));                 // ECHO: "Bb"
echo(chr([97 : 2 : 102]));           // ECHO: "ace"
echo(chr(-3));                       // ECHO: ""
echo(chr(9786), chr(9788));          // ECHO: "☺", "☼"
echo(len(chr(9788)));                // ECHO: 1
```

Note: When used with echo(), console output for character codes greater than 127 is platform dependent.

## ord
[Note: Requires version 2019.05]

Convert a character to a number representing the Unicode code point. If the parameter is not a string, ord() returns undef.

Parameters:
- ord(String) — Convert the first character of the given string to its Unicode code point.

Examples:
```openscad
echo(ord("a"));                // ECHO: 97
echo(ord("BCD"));              // ECHO: 66
echo([for (c = "Hello! 🙂") ord(c)]);
// ECHO: [72, 101, 108, 108, 111, 33, 32, 128578]

txt = "1";
echo(ord(txt) - 48, txt);      // ECHO: 1, "1"  // only converts 1 character
```

## len
Returns the number of characters in a text.

```openscad
echo(len("Hello world")); // 11
```

## Also See
- search() for text searching.

## is_string(value)
The function is_string(value) returns true if the value is a string, false otherwise.

```openscad
echo(is_string("alpha")); // true
echo(is_string(22));      // false
```

## User defined functions
To complement native functions, you can define your own functions. Some suggestions:

```openscad
//-- Lower case all chars of a string -- does not work with accented characters
function strtolower (string) =
    chr([for (s = string) let(c = ord(s)) c < 91 && c > 64 ? c + 32 : c]);

//-- Replace char (not string) in a string
function char_replace (s, old = " ", new = "_") =
    chr([for (i = [0 : len(s) - 1]) s[i] == old ? ord(new) : ord(s[i])]);

//-- Replace last chars of a string (can be used for file extension replacement of same length)
function str_rep_last (s, new = ".txt") =
    str(chr([for (i = [0 : len(s) - len(new) - 1]) ord(s[i])]), new);

//-- integer value from string ----------
// Parameters ret and i are for function internal use (recursion)
function strtoint (s, ret = 0, i = 0) =
    i >= len(s) ? ret : strtoint(s, ret * 10 + ord(s[i]) - ord("0"), i + 1);
```

Note: The use of chr() recomposes a string from an unknown number of characters defined by their code points, avoiding recursive modules previously needed before list management was available.

---

# En.Wikibooks.Org Wiki Openscad User Manual Conditional And Iterator Functions Assign Statement

# OpenSCAD User Manual: Conditional and Iterator Functions

## For loop

Evaluate each value in a range or vector, or each name in an object, applying it to the following action.

```openscad
for (variable = [start : increment : end])
for (variable = [start : end])
for (variable = [vector])
for (variable = object)
```

### For each value in a range

```openscad
for (variable = [start : increment : end])
for (variable = [start : end])
```

Note: For ranges, values are separated by colons (:) rather than commas used in vectors.

The action is evaluated for each value in the range.

- start: initial value
- increment (step): amount to increase/decrease the value, optional, default = 1
- end: stop when next value would be past end

Examples:

```openscad
for (a = [3 : 5]) echo(a);                  // 3 4 5
for (a = [3 : 0]) { echo(a); }              // 0 1 2 3
// start > end is invalid, deprecated by 2015.3

for (a = [3 : 0.5 : 5]) echo(a);            // 3 3.5 4 4.5 5
for (a = [0 : 2 : 5]) echo(a);              // 0 2 4  (a never equals end)
for (a = [3 : -2 : -1]) echo(a);            // 3 1 -1
// negative increment requires 2015.3; be sure end < start
```

### For each element of a vector

The action is evaluated for each element of the vector.

```openscad
for (a = [3, 4, 1, 5]) echo(a);             // 3 4 1 5
for (a = [0.3, PI, 1, 99]) { echo(a); }     // 0.3 3.14159 1 99

x1 = 2; x2 = 8; x3 = 5.5;
for (a = [x1, x2, x3]) { echo(a); }         // 2 8 5.5

for (a = [[1,2], 6, "s", [[3,4], [5,6]]]) echo(a);
// [1,2] 6 "s" [[3,4],[5,6]]
```

The vector can be described elsewhere, similar to “for each” in other languages.

```openscad
animals = ["elephants", "snakes", "tigers", "giraffes"];
for (animal = animals)
    echo(str("I've been to the zoo and saw ", animal));
// "I've been to the zoo and saw elephants", for each animal
```

### For each element of an object

Requires development snapshot. The action is evaluated for the name of each element of the object, in an unspecified order.

```openscad
tm = textmetrics("Hello, World!");
for (name = tm)
    echo(name, tm[name]);
```

### Notes

- for() is an operator. Operators require braces {} if more than one action is within their scope.
- Actions end with semicolons; operators do not.
- for() does not break the rule about variables having only one value within a scope. Each evaluation is given its own scope, allowing variables to have unique values. You still cannot do a = a + 1 in place.
- OpenSCAD is not iterative in the programmatic sense; for() builds a tree of objects—one branch per item—each with its own scope.

Example:

```openscad
for (i = [0 : 3])
    translate([i * 10, 0, 0]) cube(i + 1);
```

Produces a CSG tree like:

```
group() {
  group() {
    multmatrix([[1,0,0, 0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]) { cube(size=[1,1,1], center=false); }
    multmatrix([[1,0,0,10], [0,1,0,0], [0,0,1,0], [0,0,0,1]]) { cube(size=[2,2,2], center=false); }
    multmatrix([[1,0,0,20], [0,1,0,0], [0,0,1,0], [0,0,0,1]]) { cube(size=[3,3,3], center=false); }
    multmatrix([[1,0,0,30], [0,1,0,0], [0,0,1,0], [0,0,0,1]]) { cube(size=[4,4,4], center=false); }
  }
}
```

While the group() is built sequentially, all instances of the for() exist as separate entities; they do not iterate one piece of code sequentially.

### Nested for()

It is reasonable to nest multiple for() statements:

```openscad
for (z = [-180 : 45 : +180])
for (x = [10 : 5 : 50])
    rotate([0, 0, z]) translate([x, 0, 0]) cube(1);
```

Alternatively, include all ranges/vectors in the same for() operator:

```openscad
for (variable1 = <range or vector>,
     variable2 = <range or vector>)
    <do something using both variables>;
```

Nested 3-deep example:

```openscad
color_vec = ["black","red","blue","green","pink","purple"];

for (x = [-20 : 10 : 20])
for (y = [0 : 4]) color(color_vec[y])
for (z = [0, 4, 10]) {
    translate([x, y * 5 - 10, z]) cube();
}
```

Shorthand nesting for the same result:

```openscad
color_vec = ["black","red","blue","green","pink","purple"];

for (x = [-20 : 10 : 20], y = [0 : 4], z = [0, 4, 10])
    translate([x, y * 5 - 10, z]) { color(color_vec[y]) cube(); }
```

Examples using vector of vectors:

Example 1 (rotation):

```openscad
for (i = [
    [  0,  0,   0],
    [ 10, 20, 300],
    [200, 40,  57],
    [ 20, 88,  57]
]) {
    rotate(i) cube([100, 20, 20], center = true);
}
```

Example 2 (translation):

```openscad
for (i = [
    [ 0,  0,  0],
    [10, 12, 10],
    [20, 24, 20],
    [30, 36, 30],
    [20, 48, 40],
    [10, 60, 50]
]) {
    translate(i) cube([50, 15, 10], center = true);
}
```

Example 3:

```openscad
for (i = [
    [[ 0,  0,  0], 20],
    [[10, 12, 10], 50],
    [[20, 24, 20], 70],
    [[30, 36, 30], 10],
    [[20, 48, 40], 30],
    [[10, 60, 50], 40]
]) {
    translate([i[0][0], 2 * i[0][1], 0]) cube([10, 15, i[1]]);
}
```

## Intersection For Loop

Iterate over the values in a range or vector and create the intersection of objects created by each pass.

Besides creating separate instances for each pass, the standard for() also groups all these instances creating an implicit union. intersection_for() replaces this implicit union with an intersection.

intersection_for() uses the same parameters and works the same as a for loop, except for the intersection behavior.

Example 1 – loop over a range:

```openscad
intersection_for (n = [1 : 6]) {
    rotate([0, 0, n * 60]) {
        translate([5, 0, 0]) sphere(r = 12);
    }
}
```

Example 2 – rotation over a vector of vectors:

```openscad
intersection_for (i = [
    [  0,  0,   0],
    [ 10, 20, 300],
    [200, 40,  57],
    [ 20, 88,  57]
]) {
    rotate(i) cube([100, 20, 20], center = true);
}
```

## If Statement

Performs a test to determine if the actions in a sub-scope should be performed or not.

Really important: You cannot change the value of variables outside the current scope. If you assign inside braces, the new variable is lost when you exit that scope.

```openscad
if (test) scope1
if (test) { scope1 }

if (test) scope1 else scope2
if (test) { scope1 } else { scope2 }
```

Parameters:

- test: Usually a boolean expression, but can be any value or variable. Do not confuse assignment '=' with equality '=='.
- scope1: Action(s) to take when test is true.
- scope2: Action(s) to take when test is false.

Examples:

```openscad
if (b == a) cube(4);
if (b <  a) { cube(4); cylinder(6); }
if (b && a) { cube(4); cylinder(6); }
if (b != a) cube(4); else cylinder(3);
if (b)      { cube(4); cylinder(6); } else { cylinder(10, 5, 5); }
if (!true)  { cube(4); cylinder(6); } else cylinder(10, 5, 5);

if (x > y) cube(1, center = false);
else       { cube(size = 2, center = true); }

if (a == 4) {} else echo("a is not 4");

if ((b < 5) && (a > 8)) { cube(4); } else { cylinder(3); }
if (b < 5 && a > 8) cube(4); else cylinder(3);
```

Since 2015.03, variables can be assigned in any scope. Assignments are only valid within the scope in which they are defined—you cannot leak values to an outer scope.

### Nested if

The scopes of both the if() portion and the else portion can contain if() statements. This nesting can be to any depth.

```openscad
if (test1) {
    // scope1
    if (test2) { /* scope2.1 */ }
    else       { /* scope2.2 */ }
} else {
    // scope2
    if (test3) { /* scope3.1 */ }
    else       { /* scope3.2 */ }
}
```

When scope1 and scope2 contain only the if() statement, the outer sets of braces can be removed.

```openscad
if (test1)
    if (test2) { /* scope2.1 */ }
    else       { /* scope2.2 */ }
else if (test3) { /* scope3.1 */ }
else            { /* scope3.2 */ }
```

### else if

```openscad
if      (test1) { /* scope1 */ }
else if (test2) { /* scope2 */ }
else if (test3) { /* scope3 */ }
else if (test4) { /* scope4 */ }
else            { /* scope5 */ }
```

When working down the chain of tests, the first true condition selects its scope; all further tests are skipped.

Example:

```openscad
if ((k < 8) && (m > 1))      cube(10);
else if (y == 6)            { sphere(6); cube(10); }
else if (y == 7)             color("blue") sphere(5);
else if (k + m != 8)        { cylinder(15, 5, 0); sphere(8); }
else                         color("green") { cylinder(12, 5, 0); sphere(8); }
```

## Conditional ? :

A ternary operator that uses a test to determine which of two values to return.

```openscad
a = test ? TrueValue : FalseValue;
echo(test ? TrueValue : FalseValue);
```

Parameters:

- test: Usually a boolean expression, but can be any value or variable. Do not confuse assignment '=' with equality '=='.
- TrueValue: The value to return when test is true.
- FalseValue: The value to return when test is false.

A value in OpenSCAD is either:
- Number (e.g., 42)
- Boolean (e.g., true)
- String (e.g., "foo")
- Vector (e.g., [1, 2, 3])
- Undefined (undef)

This works like the ?: operator from C-like languages.

Examples:

```openscad
a = 1; b = 2;
c = (a == b) ? 4 : 5;                   // 5

a = 1; b = 2;
c = (a == b) ? "a==b" : "a!=b";         // "a!=b"

TrueValue = true;
FalseValue = false;
a = 5;
test = (a == 1);
echo(test ? TrueValue : FalseValue);    // false

L = 75;
R = 2;
test = (L / R) > 25;
TrueValue  = [test, L, R, L / R, cos(30)];
FalseValue = [test, L, R, sin(15)];
a1 = test ? TrueValue : FalseValue;     // [true, 75, 2, 37.5, 0.866025]
```

Some forms of tail-recursion elimination are supported.

### Recursive function calls

Recursive function calls are supported. Using the conditional operator ensures the recursion is terminated.

Note: There is a built-in recursion limit to prevent crashes. If the limit is hit, the function returns undef.

Example:

```openscad
// Recursion: sum values in a vector from index s to index i (inclusive)
function sumv(v, i, s = 0) = (i == s ? v[i] : v[i] + sumv(v, i - 1, s));

vec = [10, 20, 30, 40];
echo("sum vec=", sumv(vec, 2, 1));      // calculates 20 + 30 = 50
```

### Formatting complex usage

Multiple nested conditionals can be hard to read. Formatting them like multi-line, indented if/else statements is clearer.

```openscad
// Find the maximum value in a vector
function maxv(v, m = -999999999999, i = 0) =
    (i == len(v)) ? m :
    (m > v[i])    ? maxv(v, m, i + 1)
                  ? maxv(v, v[i], i + 1);

v = [7, 3, 9, 3, 5, 6];
echo("max", maxv(v));                    // ECHO: "max", 9
```

## Assign Statement

Deprecated: assign() is deprecated and will be removed in a future release. Variables can now be assigned anywhere. If you prefer this style of setting values, use the Let Statement instead.

Set variables to a new value for a sub-tree.

Parameters: The variables that should be (re-)assigned.

Example:

```openscad
for (i = [10 : 50]) {
    assign (angle = i * 360 / 20,
            distance = i * 10,
            r = i * 2) {
        rotate(angle, [1, 0, 0])
        translate([0, distance, 0])
        sphere(r = r);
    }
}
```

Equivalent without assign():

```openscad
for (i = [10 : 50]) {
    angle = i * 360 / 20;
    distance = i * 10;
    r = i * 2;
    rotate(angle, [1, 0, 0])
    translate([0, distance, 0])
    sphere(r = r);
}
```

## Let Statement

Note: Requires version 2019.05.

Set variables to a new value for a sub-tree. The parameters are evaluated sequentially and may depend on each other (unlike the deprecated assign()).

Parameters: The variables that should be set.

Example:

```openscad
for (i = [10 : 50]) {
    let (angle = i * 360 / 20,
         r = i * 2,
         distance = r * 5) {
        rotate(angle, [1, 0, 0])
        translate([0, distance, 0])
        sphere(r = r);
    }
}
```

---

# En.Wikibooks.Org Wiki Openscad User Manual Csg Modelling Difference

# OpenSCAD User Manual: CSG Modelling

This page describes Constructive Solid Geometry (CSG) operations in OpenSCAD and provides examples and usage notes.

## Boolean Overview

### 2D examples

| Operation    | Logical meaning | Geometric expression             |
|--------------|------------------|----------------------------------|
| union        | or               | circle + square                  |
| difference   | and not          | square - circle                  |
| difference   | and not          | circle - square                  |
| intersection | and              | circle - (circle - square)       |

2D OpenSCAD examples:
```openscad
union() { square(10); circle(10); }           // square or circle
difference() { square(10); circle(10); }      // square and not circle
difference() { circle(10); square(10); }      // circle and not square
intersection() { square(10); circle(10); }    // square and circle
```

### 3D examples

| Operation    | Logical meaning | Geometric expression              |
|--------------|------------------|-----------------------------------|
| union        | or               | sphere + cube                     |
| difference   | and not          | cube - sphere                     |
| difference   | and not          | sphere - cube                     |
| intersection | and              | sphere - (sphere - cube)          |

3D OpenSCAD examples:
```openscad
union() { cube(12, center=true); sphere(8); }             // cube or sphere
difference() { cube(12, center=true); sphere(8); }        // cube and not sphere
difference() { sphere(8); cube(12, center=true); }        // sphere and not cube
intersection() { cube(12, center=true); sphere(8); }      // cube and sphere
```

## union

Creates a union of all its child nodes. This is the sum of all children (logical “or”). May be used with either 2D or 3D objects, but do not mix 2D and 3D in the same CSG node.

Usage example:
```openscad
union() {
  cylinder(h = 4, r = 1, center = true, $fn = 100);
  rotate([90, 0, 0])
    cylinder(h = 4, r = 0.9, center = true, $fn = 100);
}
```

Remarks:
- Union is implicit when multiple top-level objects are listed without a wrapper. However, it is mandatory when you need to explicitly group shapes, for example inside difference() to treat the first children as a single combined object.
- It is mandatory, for all unions (explicit or implicit), that external faces to be merged not be coincident. Coincident faces can result in non-manifold geometry, warnings, missing pieces in render output, and flickering in preview. This stems from floating point comparisons and the inability to exactly represent many rotations.

Invalid example (coincident faces):
```openscad
// Invalid!
size = 10;
rotation = 17;

union() {
  rotate([rotation, 0, 0]) cube(size);
  rotate([rotation, 0, 0])
    translate([0, 0, size])
      cube([2, 3, 4]);
}
```

Corrected with a small epsilon overlap:
```openscad
// Correct!
size = 10;
rotation = 17;
eps = 0.01;

union() {
  rotate([rotation, 0, 0]) cube(size);
  rotate([rotation, 0, 0])
    translate([0, 0, size - eps])
      cube([2, 3, 4 + eps]);
}
```

## difference

Subtracts the 2nd (and all further) child nodes from the first one (logical “and not”). May be used with either 2D or 3D objects, but do not mix 2D and 3D in the same CSG node.

Usage example:
```openscad
difference() {
  cylinder(h = 4, r = 1, center = true, $fn = 100);
  rotate([90, 0, 0])
    cylinder(h = 4, r = 0.9, center = true, $fn = 100);
}
```

Notes:
- Surfaces to be removed by a difference must overlap the volume, and the subtracting (negative) shape must extend fully outside the surface it is removing. Otherwise, preview artifacts and non-manifold render warnings can occur or pieces may disappear.
- See the union section above for why a small epsilon overlap is often required.

### difference with multiple children

Usage example:
```openscad
$fn = 90;
difference() {
  cylinder(r = 5, h = 20, center = true);

  rotate([0, 140, -45])
    color("LightBlue")
      cylinder(r = 2, h = 25, center = true);

  rotate([0, 40, -50])
    cylinder(r = 2, h = 30, center = true);

  translate([0, 0, -10])
    rotate([0, 40, -50])
      cylinder(r = 1.4, h = 30, center = true);
}
```

In the next instance, the first and second children are combined with a union before subtraction:
```openscad
translate([10, 10, 0]) {
  difference() {
    union() {  // combine 1st and 2nd children
      cylinder(r = 5, h = 20, center = true);

      rotate([0, 140, -45])
        color("LightBlue")
          cylinder(r = 2, h = 25, center = true);
    }

    rotate([0, 40, -50])
      cylinder(r = 2, h = 30, center = true);

    translate([0, 0, -10])
      rotate([0, 40, -50])
        cylinder(r = 1.4, h = 30, center = true);
  }
}
```

## intersection

Creates the intersection of all child nodes, keeping only the overlapping portion (logical “and”). May be used with either 2D or 3D objects, but do not mix 2D and 3D in the same CSG node.

Usage example:
```openscad
intersection() {
  cylinder(h = 4, r = 1, center = true, $fn = 100);
  rotate([90, 0, 0])
    cylinder(h = 4, r = 0.9, center = true, $fn = 100);
}
```

## render

Warning: render() always computes the full CSG model for its subtree (even in OpenCSG preview mode), which can make previews very slow and appear to hang.

Usage:
```openscad
render(convexity = 1) {
  // geometry...
}
```

convexity:
- Integer specifying the maximum number of front/back faces a ray intersecting the object might penetrate.
- Only affects correct display in OpenCSG preview mode; it does not affect final polyhedron rendering.
- For example, a 2D shape with convexity 4 can be crossed by a ray up to 4 times. A similar interpretation applies to 3D shapes.
- Setting convexity to around 10 generally works for most cases.

---

# En.Wikibooks.Org Wiki Openscad User Manual Mathematical Functions Abs

# OpenSCAD User Manual — Mathematical Functions

Note: OpenSCAD math functions are implemented using C++ double precision floating point. Trigonometric functions use degrees (not radians). Results are subject to floating-point approximation.

## Trigonometric functions

### cos
Mathematical cosine of an angle in degrees.

Parameters:
- degrees: Decimal. Angle in degrees.

Usage:
```openscad
for (i = [0:36]) {
  translate([i * 10, 0, 0])
    cylinder(r = 5, h = cos(i * 10) * 50 + 60);
}
```

### sin
Mathematical sine of an angle in degrees.

Parameters:
- degrees: Decimal. Angle in degrees.

Usage 1:
```openscad
for (i = [0:5]) {
  echo(360 * i / 6, sin(360 * i / 6) * 80, cos(360 * i / 6) * 80);
  translate([sin(360 * i / 6) * 80, cos(360 * i / 6) * 80, 0])
    cylinder(h = 200, r = 10);
}
```

Usage 2:
```openscad
for (i = [0:36]) {
  translate([i * 10, 0, 0])
    cylinder(r = 5, h = sin(i * 10) * 50 + 60);
}
```

### tan
Mathematical tangent of an angle in degrees.

Parameters:
- degrees: Decimal. Angle in degrees.

Usage:
```openscad
for (i = [0:5]) {
  echo(360 * i / 6, tan(360 * i / 6) * 80);
  translate([tan(360 * i / 6) * 80, 0, 0])
    cylinder(h = 200, r = 10);
}
```

### acos
Arccosine (inverse cosine), returns degrees.

### asin
Arcsine (inverse sine), returns degrees.

### atan
Arctangent (inverse tangent), returns degrees in the range -90 to +90. Note: atan cannot distinguish between y/x and -y/-x. For full 360-degree angles, use atan2.

### atan2
Two-argument arctangent: atan2(y, x). Returns the full angle between the x-axis and the vector (x, y) in degrees, in the range -180 < angle <= 180.

Usage:
```openscad
atan2(5.0, -5.0);  // 135; atan(5.0/-5.0) would give -45
atan2(y, x);       // angle between (1,0) and (x,y) around the Z-axis
```

## Other Mathematical Functions

### abs
Absolute value. Returns the positive value of a signed number.

Usage:
```openscad
abs(-5.0);  // 5.0
abs(0);     // 0.0
abs(8.0);   // 8.0
```

### ceil
Ceiling. Returns the next highest integer (round up).

Usage:
```openscad
echo(ceil(4.4), ceil(-4.4));  // ECHO: 5, -4
```

### concat
Requires 2015.03 or later. Concatenate values and/or vectors. Vector arguments are flattened by one level; strings are not flattened.

Usage:
```openscad
echo(concat("a","b","c","d","e","f"));               // ["a","b","c","d","e","f"]
echo(concat(["a","b","c"], ["d","e","f"]));          // ["a","b","c","d","e","f"]
echo(concat(1,2,3,4,5,6));                           // [1,2,3,4,5,6]

// Vector of vectors (one level of nesting is removed)
echo(concat([[1],[2]], [[3]]));                      // [[1],[2],[3]]

// Add a fourth point to make a square from a triangle path
polygon(concat([[0,0],[0,5],[5,5]], [[5,0]]));

// Contrast with strings
echo(concat([1,2,3], [4,5,6]));                      // [1,2,3,4,5,6]
echo(concat("abc", "def"));                          // ["abc", "def"]
echo(str("abc","def"));                              // "abcdef"
```

Notes:
- All vector arguments lose one level of nesting.

### cross
Cross product for 3D vectors; for 2D vectors, returns the scalar z component x*v - y*u. Vectors must be both length 2 or both length 3; otherwise returns undef.

Usage:
```openscad
echo(cross([2, 3, 4], [5, 6, 7]));     // [-3, 6, -3]
echo(cross([2, 1, -3], [0, 4, 5]));    // [17, -10, 8]
echo(cross([2, 1], [0, 4]));           // 8
echo(cross([1, -3], [4, 5]));          // 17
echo(cross([2, 1, -3], [4, 5]));       // undef
echo(cross([2, 3, 4], "5"));           // undef

// Property:
 // cross(a, b) == -cross(b, a)
```

### exp
Base-e exponential: e^x.

Usage:
```openscad
echo(exp(1), exp(ln(3) * 4));  // ECHO: 2.71828, 81
```

### floor
Floor. Largest integer not greater than x.

Usage:
```openscad
echo(floor(4.4), floor(-4.4));  // ECHO: 4, -5
```

### ln
Natural logarithm.

### len
Length function. Returns the number of elements in a vector/array or the length of a string. For non-container scalars, returns undef and emits a warning.

Usage:
```openscad
str1 = "abcdef";
len_str1 = len(str1);                // 6
echo(str1, len_str1);

a = 6;
len_a = len(a);                      // undef (warning)
echo(a, len_a);

array1 = [1,2,3,4,5,6,7,8];
len_array1 = len(array1);            // 8
echo(array1, len_array1);

array2 = [[0,0],[0,1],[1,0],[1,1]];
len_array2 = len(array2);            // 4
echo(array2, len_array2);

len_array2_2 = len(array2[2]);       // 2
echo(array2[2], len_array2_2);
```

Results (illustrative):
- WARNING: len() parameter could not be converted
- ECHO: "abcdef", 6
- ECHO: 6, undef
- ECHO: [1,2,3,4,5,6,7,8], 8
- ECHO: [[0,0],[0,1],[1,0],[1,1]], 4
- ECHO: [1,0], 2

Iterating over a string:
```openscad
str2 = "4711";
for (i = [0:len(str2)-1])
  echo(str("digit ", i + 1, " : ", str2[i]));
```

Note:
- len(x) is useful for modules that accept either a scalar or a vector.

Example:
```openscad
module doIt(size) {
  if (len(size) == undef) {
    // number (or undef) — use for x,y,z
    do([size, size, size]);
  } else {
    // vector
    do(size);
  }
}

doIt(5);
doIt([5,5,5]);
```

### let
Requires 2015.03 or later. Sequential assignment of variables inside an expression, useful for readability.

Syntax:
```openscad
let (var1 = value1, var2 = f(var1), var3 = g(var1, var2)) expression
```

Usage:
```openscad
echo(let(a = 135, s = sin(a), c = cos(a)) [s, c]);  // ECHO: [0.707107, -0.707107]
```

### log
Base-10 logarithm. Example: log(1000) = 3.

### lookup
Look up a value in a table of key-value pairs, with linear interpolation for non-exact keys. Keys outside the table may return an endpoint value depending on version.

Parameters:
- key: Value to look up
- table: Vector of [key, value] pairs

Usage:
```openscad
function get_cylinder_h(p) =
  lookup(p, [
    [-200, 5],
    [ -50, 20],
    [ -20, 18],
    [ +80, 25],
    [+150,  2]
  ]);

for (i = [-100:5:+100]) {
  // echo(i, get_cylinder_h(i));
  translate([i, 0, -30])
    cylinder(r1 = 6, r2 = 2, h = get_cylinder_h(i) * 3);
}
```

### max
Maximum of parameters. With a single vector argument, returns the maximum element. Requires 2014.06 for vector form.

Parameters:
- max(n, n, ...): Two or more numbers
- max(vector): Single vector of numbers

Usage:
```openscad
max(3.0, 5.0);           // 5
max(8.0, 3.0, 4.0, 5.0); // 8
max([8, 3, 4, 5]);       // 8
```

### min
Minimum of parameters. With a single vector argument, returns the minimum element. Requires 2014.06 for vector form.

Parameters:
- min(n, n, ...): Two or more numbers
- min(vector): Single vector of numbers

Usage:
```openscad
min(3.0, 5.0);           // 3
min(8.0, 3.0, 4.0, 5.0); // 3
min([8, 3, 4, 5]);       // 3
```

### mod
Modulo is an operator (%) in OpenSCAD, not a function.

### norm
Euclidean norm (vector length). Returns numeric magnitude; len() returns element count.

Usage:
```openscad
a = [1,2,3,4,5,6];
b = "abcd";
c = [];
d = "";
e = [[1,2,3,4],[1,2,3],[1,2],[1]];

echo(norm(a));     // 9.53939
echo(norm(b));     // undef
echo(norm(c));     // 0
echo(norm(d));     // undef
echo(norm(e[0]));  // 5.47723
echo(norm(e[1]));  // 3.74166
echo(norm(e[2]));  // 2.23607
echo(norm(e[3]));  // 1
```

### pow
Power function: pow(base, exponent). Since 2021.01, you can also use the operator ^.

Parameters:
- base: Decimal
- exponent: Decimal

Usage:
```openscad
for (i = [0:5]) {
  translate([i * 25, 0, 0]) {
    cylinder(h = pow(2, i) * 5, r = 10);
    echo(i, pow(2, i));
  }
}

echo(pow(10, 2));       // 100
echo(pow(10, 3));       // 1000
echo(pow(125, 1/3));    // 5  (cube root)
```

### rands
Random number generator. Returns a constant vector of pseudo-random doubles in [min, max). For a single number, index [0]. Optional seed for repeatability.

Parameters:
- min_value: Minimum value (inclusive)
- max_value: Maximum value (exclusive)
- value_count: Number of values
- seed_value: Optional seed (rounded to integer in versions before late 2015)

Usage:
```openscad
// single number
single_rand = rands(0, 10, 1)[0];
echo(single_rand);

// vector of 4 numbers with seed
seed = 42;
random_vect = rands(5, 15, 4, seed);
echo("Random Vector: ", random_vect);

// example use
sphere(r = 5);
for (i = [0:3]) {
  rotate(360 * i / 4) {
    translate([10 + random_vect[i], 0, 0])
      sphere(r = random_vect[i] / 2);
  }
}

// Get a vector of integers between 1 and 10 inclusive by widening the range
function irands(minimum, maximum, n) =
  let(floats = rands(minimum, maximum + 1, n))
    [ for (f = floats) floor(f) ];

echo(irands(1, 10, 5));  // e.g., [9, 6, 2, 4, 1]
```

### round
Round to nearest integer, with ties away from zero for positive inputs and toward zero for negative inputs as per behavior shown below.

Usage:
```openscad
round(5.4);   // 5
round(5.5);   // 6
round(5.6);   // 6
round(-5.4);  // -5
round(-5.5);  // -6
round(-5.6);  // -6
```

### sign
Signum function. Returns -1, 0, or +1 depending on the sign of the input.

Parameters:
- x: Decimal. Value to test.

Usage:
```openscad
sign(-5.0);  // -1.0
sign(0);     // 0.0
sign(8.0);   // 1.0
```

### sqrt
Square root.

Usage:
```openscad
translate([sqrt(100), 0, 0])
  sphere(100);
```

## Infinities and NaNs

OpenSCAD follows IEEE 754 behavior from the underlying C++ math library:
- Infinite values: Inf, -Inf
- Not-a-Number: NaN (e.g., 0/0, sqrt(-1))

Examples (behavior observed in late 2015 tests):
```
0/0: nan
-0/0: nan
0/-0: nan
1/0: inf
1/-0: -inf
-1/0: -inf
-1/-0: inf

sin(1/0): nan
cos(1/0): nan
tan(1/0): nan

asin(1/0): nan
acos(1/0): nan
atan(1/0): 90
atan(-1/0): -90
atan2(1/0, -1/0): 135

ln(1/0): inf
ln(-1/0): nan
log(1/0): inf
log(-1/0): nan

ceil(-1/0): -inf
ceil(1/0): inf
floor(-1/0): -inf
floor(1/0): inf
round(1/0): inf
round(-1/0): -inf

sign(1/0): 1
sign(-1/0): -1

sqrt(1/0): inf
sqrt(-1/0): nan

exp(1/0): inf
exp(-1/0): 0

max(-1/0, 1/0): inf
min(-1/0, 1/0): -inf

pow(2, 1/0): inf
pow(2, -1/0): 0
```

---

# En.Wikibooks.Org Wiki Openscad User Manual List Comprehensions Each

# OpenSCAD User Manual — List Comprehensions

[Note: Requires version 2015.03]

## Basic Syntax

List comprehensions provide a flexible way to generate lists using the general syntax:

```openscad
[ list-definition expression ]
```

Supported elements for constructing the list definition:

- for (i = sequence): Iteration over a range or an existing list.
- for (init; condition; next): Simple recursive call represented as a C-style for.
- each: Takes a sequence value as argument, and adds each element to the list being constructed. each x is equivalent to for (i = x) i.
- if (condition): Selection criteria; when true, the expression is calculated and added to the result list.
- let (x = value): Local variable assignment.

### Multiple generator expressions

[Note: Requires version 2019.05]

The list comprehension syntax is generalized to allow multiple expressions. This allows constructing lists from multiple sub-lists generated by different list comprehension expressions without concat.

```openscad
steps = 50;

points = [
  // first expression generating the points in the positive Y quadrant
  for (a = [0 : steps]) [ a, 10 * sin(a * 360 / steps) + 10 ],

  // second expression generating the points in the negative Y quadrant
  for (a = [steps : -1 : 0]) [ a, 10 * cos(a * 360 / steps) - 20 ],

  // additional list of fixed points
  [ 10, -3 ],
  [ 3, 0 ],
  [ 10, 3 ]
];

polygon(points);
```

## for

The for element defines the input values for the list generation. The syntax is the same as used by the for iterator.

The sequence to the right of the equals sign can be any list. The for element iterates over all members of the list. The variable on the left of the equals sign takes on the value of each member of the sequence in turn. This value can then be processed in the child of the for element, and each result becomes a member of the final list. If the sequence has more than one dimension, for iterates over the first dimension only. Deeper dimensions can be accessed by nesting for elements.

Common usage patterns:

```openscad
[ for (i = [start : step : end]) i ]
```

Examples:

```openscad
// generate a list with all values defined by a range
list1 = [ for (i = [0 : 2 : 10]) i ];
echo(list1); // ECHO: [0, 2, 4, 6, 8, 10]

// extract every second character of a string
str = "SomeText";
list2 = [ for (i = [0 : 2 : len(str) - 1]) str[i] ];
echo(list2); // ECHO: ["S", "m", "T", "x"]

// indexed list access, using function to map input values to output values
function func(x) = x < 1 ? 0 : x + func(x - 1);
input = [1, 3, 5, 8];
output = [for (a = [ 0 : len(input) - 1 ]) func(input[a]) ];
echo(output); // ECHO: [1, 6, 15, 36]
```

```openscad
[ for (i = [a, b, c, ...]) i ]
```

Examples:

```openscad
// iterate over an existing list
friends = ["John", "Mary", "Alice", "Bob"];
list = [ for (i = friends) len(i)];
echo(list); // ECHO: [4, 4, 5, 3]

// map input list to output list
list = [ for (i = [2, 3, 5, 7, 11]) i * i ];
echo(list); // ECHO: [4, 9, 25, 49, 121]

// calculate Fibonacci numbers
function func(x) = x < 3 ? 1 : func(x - 1) + func(x - 2);
input = [7, 10, 12];
output = [for (a = input) func(a) ];
echo(output); // ECHO: [13, 55, 144]
```

```openscad
[ for (c = "String") c ]
```

[Note: Requires version 2019.05]

Example:

```openscad
echo([ for (c = "String") c ]); // ECHO: ["S", "t", "r", "i", "n", "g"]
```

```openscad
[ for (a = inita, b = initb, ...; condition; a = nexta, b = nextb, ...) expr ]
```

Generator for expressing a simple recursive call as a C-style for loop.

[Note: Requires version 2019.05]

Recursive equivalent:

```openscad
function f(a, b, ...) =
  condition ? concat([expr], f(nexta, nextb, ...)) : [];
f(inita, initb, ...);
```

Examples:

```openscad
echo( [for (a = 0, b = 1; a < 5; a = a + 1, b = b + 2) [ a, b * b ] ] );
// ECHO: [[0, 1], [1, 9], [2, 25], [3, 49], [4, 81]]

// Generate fibonacci sequence
echo([for (a = 0, b = 1; a < 1000; x = a + b, a = b, b = x) a]);
// ECHO: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

// Cumulative sum of values in v
function cumsum(v) = [for (a = v[0]-v[0], i = 0; i < len(v); a = a+v[i], i = i+1) a+v[i]];
echo(cumsum([1, 2, 3, 4]));                // ECHO: [1, 3, 6, 10]
echo(cumsum([[1, 1], [2, 2], [3, 3]]));    // ECHO: [[1, 1], [3, 3], [6, 6]]
```

## each

[Note: Requires version 2019.05]

each embeds the values of a list given as argument directly, effectively unwrapping the argument list.

```openscad
// Without using "each", a nested list is generated
echo([ for (a = [1 : 4]) [a, a * a] ]);
// ECHO: [[1, 1], [2, 4], [3, 9], [4, 16]]

// Adding "each" unwraps the inner list, producing a flat list as result
echo([ for (a = [1 : 4]) each [a, a * a] ]);
// ECHO: [1, 1, 2, 4, 3, 9, 4, 16]
```

each unwraps ranges and helps to build more general for lists when combined with multiple generator expressions.

```openscad
A = [-2, each [1:2:5], each [6:-2:0], -1];
echo(A);                         // ECHO: [-2, 1, 3, 5, 6, 4, 2, 0, -1]
echo([ for (a = A) 2 * a ]);     // ECHO: [-4, 2, 6, 10, 12, 8, 4, 0, -2]
```

## if

The if element allows selecting whether the expression should be evaluated and added to the result list. In the simplest case, this allows filtering of a list.

```openscad
[ for (i = list) if (condition(i)) i ]
```

When the condition evaluates to true, the expression i is added to the result list.

Example:

```openscad
list = [ for (a = [ 1 : 8 ]) if (a % 2 == 0) a ];
echo(list); // ECHO: [2, 4, 6, 8]
```

Note that the if element cannot be inside an expression; it must be at the top level of the comprehension.

Example:

```openscad
// from the input list include all positive odd numbers
// and also all even number divided by 2
list = [-10:5];
echo([for(n=list) if(n%2==0 || n>=0) n%2==0 ? n/2 : n ]);
// ECHO: [-5, -4, -3, -2, -1, 0, 1, 1, 3, 2, 5]

// echo([for(n=list) n%2==0 ? n/2 : if(n>=0) n ]); // this would be a syntax error
```

## if/else

[Note: Requires version 2019.05]

The if-else construct is equivalent to the conditional expression ?: except that it can be combined with filter if.

```openscad
[ for (i = list) if (condition(i)) x else y ]
```

When the condition returns true, x is added to the result list; otherwise y is added.

```openscad
// even numbers are halved, positive odd numbers are preserved, negative odd numbers are eliminated
echo([for (a = [-3:5]) if (a % 2 == 0) [a, a/2] else if (a > 0) [a, a] ]);
// ECHO: [[-2, -1], [0, 0], [1, 1], [2, 1], [3, 3], [4, 2], [5, 5]];
```

The same filter using the conditional operator is possible but more cryptic:

```openscad
// even numbers are halved, positive odd numbers are preserved, negative odd numbers are eliminated
echo([for (a = [-3:5]) if (a % 2 == 0 || (a % 2 != 0 && a > 0))
       a % 2 == 0 ? [a, a / 2] : [a, a] ]);
// ECHO: [[-2, -1], [0, 0], [1, 1], [2, 1], [3, 3], [4, 2], [5, 5]];
```

To bind an else expression to a specific if, use parentheses:

```openscad
// even numbers are dropped, multiples of 4 are substituted by -1
echo([for(i=[0:10]) if(i%2==0) (if(i%4==0) -1 ) else i]);
// ECHO: [-1, 1, 3, -1, 5, 7, -1, 9]

// odd numbers are dropped, multiples of 4 are substituted by -1
echo([for(i=[0:10]) if(i%2==0) if(i%4==0) -1 else i]);
// ECHO: [-1, 2, -1, 6, -1, 10]
```

## let

The let element allows sequential assignment of variables inside a list comprehension definition.

```openscad
[ for (i = list) let (assignments) a ]
```

Example:

```openscad
list = [ for (a = [ 1 : 4 ]) let (b = a*a, c = 2 * b) [ a, b, c ] ];
echo(list); // ECHO: [[1, 1, 2], [2, 4, 8], [3, 9, 18], [4, 16, 32]]
```

## Nested loops

There are different ways to define nested loops. Defining multiple loop variables inside one for element and multiple for elements both produce flat result lists. To generate nested result lists, an additional [ ] markup is required.

```openscad
// nested loop using multiple variables
flat_result1 = [ for (a = [ 0 : 2 ], b = [ 0 : 2 ]) a == b ? 1 : 0 ];
echo(flat_result1); // ECHO: [1, 0, 0, 0, 1, 0, 0, 0, 1]

// nested loop using multiple for elements
flat_result2 = [ for (a = [ 0 : 2 ]) for (b = [0 : 2]) a == b ? 1 : 0 ];
echo(flat_result2); // ECHO: [1, 0, 0, 0, 1, 0, 0, 0, 1]

// nested loop to generate a bi-dimensional matrix
identity_matrix = [ for (a = [ 0 : 2 ]) [ for (b = [ 0 : 2 ]) a == b ? 1 : 0 ] ];
echo(identity_matrix); // ECHO: [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
```

## Advanced Examples

### Generating vertices for a polygon

Using list comprehension, a parametric equation can be calculated at a number of points to approximate many curves, such as the following example for an ellipse (using polygon()):

```openscad
sma = 20; // semi-minor axis
smb = 30; // semi-major axis

polygon(
  [ for (a = [0 : 5 : 359])
    [ sma * sin(a), smb * cos(a) ] ]
);
```

### Flattening a nested vector

List comprehension can be used in a user-defined function to perform tasks on or for vectors. Here is a user-defined function that flattens a nested vector.

```openscad
// input : nested list
// output: list with the outer level nesting removed
function flatten(l) = [ for (a = l) for (b = a) b ] ;

nested_list = [ [ 1, 2, 3 ], [ 4, 5, 6 ] ];
echo(flatten(nested_list)); // ECHO: [1, 2, 3, 4, 5, 6]
```

### Sorting a vector

Even a complicated algorithm like Quicksort becomes doable with for(), if(), let() and recursion:

```openscad
// input : list of numbers
// output: sorted list of numbers
function quicksort(arr) =
  !(len(arr) > 0) ? [] :
  let(
    pivot  = arr[floor(len(arr)/2)],
    lesser = [ for (y = arr) if (y < pivot) y ],
    equal  = [ for (y = arr) if (y == pivot) y ],
    greater= [ for (y = arr) if (y > pivot) y ]
  )
  concat( quicksort(lesser), equal, quicksort(greater) );

// use seed in rands() to get reproducible results
unsorted = [for (a = rands(0, 10, 6, 3)) ceil(a)];
echo(unsorted);             // ECHO: [6, 1, 8, 9, 3, 2]
echo(quicksort(unsorted));  // ECHO: [1, 2, 3, 6, 8, 9]
```

### Selecting elements of a vector

select() performs selection and reordering of elements into a new vector.

```openscad
function select(vector, indices) = [ for (index = indices) vector[index] ];

vector1   = [[0,0],[1,1],[2,2],[3,3],[4,4]];
selector1 = [4,0,3];

vector2 = select(vector1, selector1);        // [[4, 4], [0, 0], [3, 3]]
vector3 = select(vector1,[0,2,4,4,2,0]);     // [[0, 0], [2, 2], [4, 4],[4, 4], [2, 2], [0, 0]]

// range also works as indices
vector4 = select(vector1, [4:-1:0]);         // [[4, 4], [3, 3], [2, 2], [1, 1], [0, 0]]
```

### Concatenating two vectors

Using indices:

```openscad
function cat(L1, L2) = [for (i=[0:len(L1)+len(L2)-1]) i < len(L1)? L1[i] : L2[i-len(L1)]] ;
echo(cat([1,2,3],[4,5])); // [1, 2, 3, 4, 5]
```

Without using indices:

```openscad
function cat(L1, L2) = [for(L=[L1, L2], a=L) a];
echo(cat([1,2,3],[4,5])); // [1, 2, 3, 4, 5]
```

---

# En.Wikibooks.Org Wiki Openscad User Manual Modifier Characters Background Modifier

# OpenSCAD User Manual — Modifier Characters

Modifier characters change the appearance or behavior of child nodes. They are especially useful for debugging to highlight specific objects or to include/exclude them from rendering.

## Advanced concept: Preview vs. Render behavior

OpenSCAD uses different libraries for different operations, which can affect how modifiers appear during preview (F5):

- Traditional transforms (translate, rotate, scale, mirror, multimatrix) are previewed via OpenGL.
- Some advanced transforms like resize perform a CGAL operation, affecting the underlying object like a CSG operation.

This can lead to non-intuitive highlighting with the "#" and "%" modifiers (e.g., highlighting the pre-resized object, but post-scaled object).

Note: Color changes triggered by modifier characters appear only in Compile (Preview) mode, not in Compile and Render (CGAL) mode.

## Background Modifier (%)

Ignore this subtree during normal rendering and draw it in transparent gray. All transformations are still applied to nodes in this tree.

- In Boolean operations like difference(), using % on the first child can be surprising: the object is drawn in gray but not used as the base of the difference.

Usage:
```openscad
% {
  // ...
}
```

Example:
```openscad
difference() {
  cylinder(h = 12, r = 5, center = true, $fn = 100);                      // first object to be subtracted
  rotate([90, 0, 0]) cylinder(h = 15, r = 1, center = true, $fn = 100);   // second object to be subtracted
  %rotate([0, 90, 0]) cylinder(h = 15, r = 3, center = true, $fn = 100);
}
```

## Debug Modifier (#)

Use this subtree as usual in the rendering process and also draw it unmodified in transparent pink.

Usage:
```openscad
# {
  // ...
}
```

Example:
```openscad
difference() {
  // start objects
  cylinder(h = 12, r = 5, center = true, $fn = 100);                      
  #rotate([90, 0, 0]) cylinder(h = 15, r = 1, center = true, $fn = 100);  
  #rotate([0, 90, 0]) cylinder(h = 15, r = 3, center = true, $fn = 100);  
}
```

## Root Modifier (!)

Ignore the rest of the design and use this subtree as the design root.

Usage:
```openscad
! {
  // ...
}
```

Example:
```openscad
difference() {
  cube(10, center = true);
  translate([0, 0, 5]) {
    !rotate([90, 0, 0]) {
      #cylinder(r = 2, h = 20, center = true, $fn = 40);
    }
  }
}
```

Note: In the example above, rotate() is executed because it's inside the root-marked subtree, but the surrounding translate() has no effect.

## Disable Modifier (*)

Completely ignore this subtree. Useful for temporarily disabling parts of the design in a structure-aware way.

Usage:
```openscad
* {
  // ...
}
```

Example:
```openscad
difference() {
  cube(10, center = true);
  translate([0, 0, 5]) {
    rotate([0, 90, 0]) {
      cylinder(r = 2, h = 20, center = true, $fn = 40);
    }
    *rotate([90, 0, 0]) {
      #cylinder(r = 2, h = 20, center = true, $fn = 40);
    }
  }
}
```

Note: Unlike traditional comments, the disable modifier respects hierarchy, making it easier to disable large subtrees without hunting for their end.

## Echo statements

Print text and values to the Console during compilation. Useful for debugging. Numeric values are rounded to 5 significant digits. A common pattern is label=value for clarity.

Example:
```openscad
my_h = 50;
my_r = 100;

echo("This is a cylinder with h=", my_h, " and r=", my_r);
echo(my_h = my_h, my_r = my_r); // labeled shortcut

cylinder(h = my_h, r = my_r);
```

Console output:
```
ECHO: "This is a cylinder with h=", 50, " and r=", 100
ECHO: my_h = 50, my_r = 100
```

---

# En.Wikibooks.Org Wiki Openscad User Manual Mathematical Operators Logical Operators

# OpenSCAD User Manual — Mathematical and Logical Operators

The following documents arithmetic, relational, logical, conditional, vector, and matrix operations in OpenSCAD. Examples are provided in OpenSCAD code blocks.

## Scalar arithmetic operators

The scalar arithmetic operators take numbers as operands and produce a new number.

| Operator | Description |
|---|---|
| + | add |
| - | subtract |
| * | multiply |
| / | divide |
| % | modulo |
| ^ | exponent (requires version 2021.01 or newer) |
| - (prefix) | unary negation |

Notes:
- Prior to version 2021.01, use the builtin function pow() instead of the ^ exponent operator.
- The - operator can also be used as a prefix operator to negate a number.

Example:

```openscad
a = [ for (i = [0:10]) i % 2 ];
echo(a); // ECHO: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
// A number modulo 2 is zero if even and one if odd.
```

## Binary arithmetic (bitwise)

[Note: Requires a development snapshot.]

Numbers are converted to 64-bit signed integers for binary arithmetic, and then converted back. OpenSCAD numbers have 53 bits of precision; binary arithmetic exceeding 2^53 will be imprecise.

| Operator | Description |
|---|---|
| \| | bitwise OR |
| & | bitwise AND |
| << | left shift |
| >> | right shift (sign preserving) |
| ~ | unary bitwise NOT |

## Relational operators

Relational operators produce a boolean result from two operands.

| Operator | Description |
|---|---|
| < | less than |
| <= | less or equal |
| == | equal |
| != | not equal |
| >= | greater or equal |
| > | greater than |

Behavior notes:
- Numbers: standard numeric comparisons.
- Strings: compared alphabetically (e.g., "ab" > "aa" > "a").
- Booleans: true > false. In comparisons between a Boolean and a number, true is treated as 1 and false as 0. Other inequality tests involving Booleans return false.
- Vectors: equality (==) returns true only if vectors are identical; all inequality comparisons (<, <=, >, >=) involving one or two vectors return false (e.g., [1] < [2] is false).
- Dissimilar types: test as unequal with == and !=; inequality comparisons (<, <=, >, >=) result in false, except for Boolean–number comparisons as noted above.
- [1] and 1 are different types, so [1] == 1 is false.
- undef equals only itself; inequality comparisons involving undef are false.
- nan does not equal anything (not even itself); all inequality tests with nan produce false.

## Logical operators

All logical operators take Booleans as operands and produce a Boolean. Non-Boolean quantities are converted to Booleans before evaluation.

| Operator | Description |
|---|---|
| && | logical AND |
| \|\| | logical OR |
| ! | logical unary NOT |

Notes:
- Non-empty vectors are truthy. Since [false] is true, the expression false || [false] is also true.
- Logical operators treat vectors differently than relational operators: [1, 1] > [0, 2] is false, but [false, false] && [false, false] is true.

## Conditional operator

The ?: operator conditionally evaluates one of two expressions, like in C-like languages.

Syntax: condition ? expr_if_true : expr_if_false

Example:

```openscad
a = 1;
b = 2;
c = (a == b) ? 4 : 5; // If a equals b, c = 4; otherwise, c = 5.
```

## Vector–number operators

The vector–number operators take a vector and a number as operands and produce a new vector.

| Operator | Description |
|---|---|
| number * vector | multiply all vector elements by number |
| vector / number | divide all vector elements by number |

Example:

```openscad
L = [1, [2, [3, "a"]]];
echo(5 * L); // ECHO: [5, [10, [15, undef]]]
```

## Vector operators

The vector operators take vectors as operands and produce a new vector.

| Operator | Description |
|---|---|
| + | add element-wise |
| - | subtract element-wise |
| - (prefix) | element-wise unary negation |

Notes:
- Using + or - with vector operands of different sizes produces a result vector sized to the smaller operand.

Example:

```openscad
L1 = [1, [2, [3, "a"]]];
L2 = [1, [2, 3]];

echo(L1 + L1); // ECHO: [2, [4, [6, undef]]]
echo(L1 + L2); // ECHO: [2, [4, undef]]
```

## Vector dot-product operator

If both operands of multiplication are simple vectors (numbers only), the result is a number according to the dot product:

c = u * v = sum over i of (u_i * v_i)

If the operand sizes don’t match, the result is undef.

## Matrix multiplication

If one or both operands of multiplication are matrices, the result follows linear algebra rules.

- Matrix–matrix (A is n×m, B is m×p):
  - C = A * B is n×p with elements C_ij = sum over k=0..m-1 of (A_ik * B_kj).
  - B * A results in undef unless n = p.

- Matrix–vector (A is n×m, v is size m):
  - u = A * v is a vector of size n with elements u_i = sum over k=0..m-1 of (A_ik * v_k).
  - This corresponds to a matrix times a column vector.

- Vector–matrix (v is size n, A is n×m):
  - u = v * A is a vector of size m with elements u_j = sum over k=0..n-1 of (v_k * A_kj).
  - This corresponds to a row vector times a matrix.

Matrix multiplication is not commutative: A*B ≠ B*A, and A*v ≠ v*A.

---

# En.Wikibooks.Org Wiki Openscad User Manual Other Language Features $Fa

# OpenSCAD User Manual: Other Language Features

## Special variables

Special variables provide an alternate means of passing arguments to modules and functions. All variables starting with a `$` are special variables. Modules and functions see all outside variables in addition to those passed as arguments or defined internally.

- Special variable names are `$` followed by simple characters and underscores `[a-zA-Z0-9_]`. High-ASCII or Unicode characters are not allowed.
- Regular variables are assigned at compile time (static for all calls).
- Special variables pass along their value from within the scope from which the module or function is called, so they can differ for each call.

Example showing differences between regular and special variables and their scoping:

```openscad
regular = "regular global";
$special = "special global";

module show()
    echo(" in show ", regular," ", $special );

echo (" outside ", regular," ", $special );
// ECHO: " outside ", "regular global", " ", "special global"

for ( regular = [0:1] ){
    echo("in regular loop ", regular," ", $special );
    show();
}
// ECHO: "in regular loop ", 0, " ", "special global"
// ECHO: " in show ", "regular global", " ", "special global"
// ECHO: "in regular loop ", 1, " ", "special global"
// ECHO: " in show ", "regular global", " ", "special global"

for ( $special = [5:6] ){
    echo("in special loop ", regular," ", $special );
    show();
}
// ECHO: "in special loop ", "regular global", " ", 5
// ECHO: " in show ", "regular global", " ", 5
// ECHO: "in special loop ", "regular global", " ", 6
// ECHO: " in show ", "regular global", " ", 6

show();
// ECHO: " in show ", "regular global", " ", "special global"
```

Several special variables are predefined by OpenSCAD.

### Circle resolution: $fa, $fs, and $fn

These special variables control the number of facets used to generate arcs:

- `$fa`: minimum angle per fragment (defaults to 12). A full circle uses at most `360 / $fa` fragments. Minimum allowed is `0.01` (lower values warn).
- `$fs`: minimum size per fragment (defaults to 2). Governs small circles so they use fewer fragments than `$fa` would imply. Minimum allowed is `0.01` (lower values warn).
- `$fn`: explicit number of fragments (defaults to 0). If greater than 0, it overrides `$fa` and `$fs`. Higher values increase CPU and memory.

Guidance:
- Keep `$fn` small during design; increase for the final render.
- `$fn > 128` is generally not recommended unless necessary; `< 50` is advisable for performance.
- Use different values for preview and render:
  
```openscad
$fn = $preview ? 32 : 64;
```

Tip: To get axis-aligned integer bounding boxes for circles/cylinders/spheres, choose `$fn` divisible by 4.

When `$fa` and `$fs` determine the fragment count for a circle, OpenSCAD never uses fewer than 5 fragments.

C code used to determine number of fragments:

```c
int get_fragments_from_r(double r, double fn, double fs, double fa) {
    if (r < GRID_FINE) return 3;
    if (fn > 0.0) return (int)(fn >= 3 ? fn : 3);
    return (int)ceil(fmax(fmin(360.0 / fa, r*2*M_PI / fs), 5));
}
```

OpenSCAD expression to inspect the computation (set r to your radius):

```openscad
echo(
    n = ($fn > 0 ? ($fn >= 3 ? $fn : 3) : ceil(max(min(360/$fa, r*2*PI/$fs), 5))),
    a_based = 360/$fa,
    s_based = r*2*PI/$fs
);
```

Notes:
- Spheres are sliced by the fragment count of a circle with the sphere’s radius. The pole typically forms a pentagon.
- Cylinders use the greater of the two radii to determine fragment count.
- `$fa`, `$fs`, `$fn` affect built primitives and DXF arcs/circles; they do not affect STL imports.

Examples:

```openscad
// High-resolution sphere by resetting special variable
$fs = 0.01;
sphere(2);
```

```openscad
// Passing the special variable as a parameter
sphere(2, $fs = 0.01);
```

```openscad
// Scaling the special variable
sphere(2, $fs = $fs * 0.01);
```

## Animation: $t

The `$t` variable is a time parameter useful for animation. Typically use `$t * 360` for full cycles.

- Start animation via View → Animate, setting FPS and Steps.
- `$t` runs from 0 to `(1 - 1/Steps)` and never reaches 1 to avoid frame duplication “hitching.”
- No variable distinguishes “first frame” (`$t=0`) from “not animating,” so use `$t=0` as the rest position.

### Simple harmonic motion

```openscad
translate([0, 0, 10*sin($t*360)]) sphere(2);
```

Oscillates a sphere between -10 and +10 on the Z-axis.

### Rotation

```openscad
rotate([0, 0, $t*360]) square(5);
```

Rotate square around a corner on Z.

Rotate about center:

```openscad
rotate([0, 0, $t*360]) square(5, center=true);
```

### Part-rotation

All animated parts cycle together across the same `$t` span; different apparent speeds can be achieved by scaling angles, enabling meshing gear effects.

```openscad
rotate([0, 0, $t*360/17]) gear(teeth=17);
```

```openscad
rotate([0, 0, -$t*360/31]) gear(teeth=31);
```

### Circular orbit

```openscad
rotate([0, 0, $t*360]) translate([10, 0]) square(5, center=true);
```

### Circular orbit without rotation

```openscad
rotate([0, 0, $t*360])
translate([9, 0])
rotate([0, 0, -$t*360])
square(5, center=true);
```

### Elliptical orbit

```openscad
translate([10*sin($t*360), 20*cos($t*360)])
square(2, center=true);
```

Note: Using translate alone does not rotate the object.

### Elliptical motion

```openscad
e = 10;
rotate([0, 0, $t*360])
translate([e, 0])
rotate([0, 0, -$t*720])
square([2*e, 2], center=true);
```

Export frames as PNG and convert to GIF:

```
convert -delay 10 -loop 0 *.png myimage.gif
```

## Viewport: $vpr, $vpt, $vpf, $vpd

Contain the viewport state at render time. During animation, they update per frame. Moving the viewport alone doesn’t update the variables.

- `$vpr`: rotation
- `$vpt`: translation (not affected by rotate/zoom)
- `$vpf`: field of view (requires 2021.01)
- `$vpd`: camera distance (requires 2015.03)

Example: size varies with view angle (active animation loop required; it does not need to use `$t`):

```openscad
cube([10, 10, $vpr[0] / 10]);
```

All four variables are writable at top-level in the main file to affect the viewport (requires 2015.03).

Example: simple 360° Z-rotation in animation mode:

```openscad
$vpr = [0, 0, $t * 360];
```

The Paste Viewport Rotation/Translation command copies the current viewport values (not the variable values).

## Execution mode: $preview

[Note: Requires 2019.05]

- `$preview = true` in OpenCSG preview (F5).
- `$preview = false` in render (F6).

Use it to reduce detail for faster previews:

```openscad
$fn = $preview ? 12 : 72;
sphere(r = 1);
```

The render module does not affect `$preview`:

```openscad
render() {
    $fn = $preview ? 12 : 72;
    sphere(r = 1);
}
```

Command-line behavior: `$preview = true` only when generating PNG with OpenCSG; it’s false for STL, DXF, SVG (CGAL), CSG, and ECHO. Override on the command line with `-D`.

## Echo module

The `echo()` module prints to the Console (compilation window). Handy for debugging. Numeric values are rounded to 5 significant digits.

Usage examples:

```openscad
my_h = 50;
my_r = 100;

echo("This is a cylinder with h=", my_h, " and r=", my_r);
echo(my_h = my_h, my_r = my_r); // shortcut

cylinder(h = my_h, r = my_r);

// Console:
// ECHO: "This is a cylinder with h=", 50, " and r=", 100
// ECHO: my_h = 50, my_r = 100
```

### Rounding examples

```openscad
a = 1.0;
b = 1.000002;

echo(a);
echo(b);

if (a == b) {
    echo("a==b");
} else if (a > b) {
    echo("a>b");
} else if (a < b) {
    echo("a<b");
} else {
    echo("???");
}

// Console:
// ECHO: 1
// ECHO: 1
// ECHO: "a<b"
```

### Small and large numbers

```openscad
c = 1000002;
d = 0.000002;
echo(c); // 1e+06
echo(d); // 2e-06
```

### HTML

HTML output in the console is not officially supported; behavior depends on version.

## Echo function

[Note: Requires 2019.05]

`echo()` can be used in expression context to print values while evaluating, including within recursive functions. Output occurs before evaluation.

```openscad
a = 3;
b = 5;

// echo() prints values before evaluating the expression
r1 = echo(a, b) a * b;       // ECHO: 3, 5

// using let, it's easy to output the result
r2 = let(r = 2 * a * b) echo(r) r; // ECHO: 30

// show results
echo(r1, r2);                // ECHO: 15, 30
```

Example printing both inputs and result of recursive sum:

```openscad
v = [4, 7, 9, 12];

function result(x) = echo(result = x) x;

function sum(x, i = 0) =
    echo(str("x[", i, "]=", x[i]))
    result(len(x) > i ? x[i] + sum(x, i + 1) : 0);

echo("sum(v) = ", sum(v));

// ECHO: "x[0]=4"
// ECHO: "x[1]=7"
// ECHO: "x[2]=9"
// ECHO: "x[3]=12"
// ECHO: "x[4]=undef"
// ECHO: result = 0
// ECHO: result = 12
// ECHO: result = 21
// ECHO: result = 28
// ECHO: result = 32
// ECHO: "sum(v) = ", 32
```

## render

Forces mesh generation even in preview mode (useful when boolean operations are slow or to avoid preview artifacts). Often used with `convexity`.

```openscad
render(convexity = 2)
difference() {
    cube([20, 20, 150], center = true);
    translate([-10, -10, 0])      cylinder(h = 80, r = 10, center = true);
    translate([-10, -10, +40])    sphere(r = 10);
    translate([-10, -10, -40])    sphere(r = 10);
}
```

## surface

Reads heightmap data from text or image files.

Parameters:
- `file` (string): Path to heightmap data.
- `center` (bool): Center on X/Y if true; else placed in positive quadrant. Default: false.
- `invert` (bool): Invert image color → height mapping. No effect for text data. Default: false. The resulting geometry is positioned with its top at z = 0, with a thin “footprint” layer (1 unit thick) added just below.
- `convexity` (int): Maximum number of front/back faces a ray might penetrate (for correct OpenCSG preview only; no effect on final render). [Requires 2015.03]

### Text file format

Text-based heightmaps are matrices of numbers (heights). Rows map to Y, columns to X, with unit spacing. Numbers are separated by spaces or tabs. Empty lines and lines beginning with `#` are ignored.

### Images

[Requires 2015.03]

- Currently only PNG is supported.
- Alpha channel is ignored.
- Height computed from sRGB linear luminance: `Y = 0.2126R + 0.7152G + 0.0722B`.
- Heights are scaled to range 0–100.
- A 1-unit thick “footprint” layer is added below the heightmap.

### Examples

Example 1 (text heightmap):

```openscad
// surface.scad
surface(file = "surface.dat", center = true, convexity = 5);
%translate([0,0,5]) cube([10,10,10], center = true);
```

surface.dat:

```
#surface.dat
10 9 8 7 6 5 5 5 5 5
9 8 7 6 6 4 3 2 1 0
8 7 6 6 4 3 2 1 0 0
7 6 6 4 3 2 1 0 0 0
6 6 4 3 2 1 1 0 0 0
6 6 3 2 1 1 1 0 0 0
6 6 2 1 1 1 1 0 0 0
6 6 1 0 0 0 0 0 0 0
3 1 0 0 0 0 0 0 0 0
3 0 0 0 0 0 0 0 0 0
```

Example 2 (generated data + variations):

```
# example010.dat generated using Octave/Matlab:
d = (sin(1:0.2:10)' * cos(1:0.2:10)) * 10;
save("-ascii", "example010.dat", "d");
```

```openscad
// original surface
surface(file = "example010.dat", center = true, convexity = 5);

// rotated surface
translate([70, 0, 0])
rotate(45, [0, 0, 1])
surface(file = "example010.dat", center = true, convexity = 5);

// intersection
translate([35, 60, 0])
intersection() {
    surface(file = "example010.dat", center = true, convexity = 5);
    rotate(45, [0, 0, 1])
    surface(file = "example010.dat", center = true, convexity = 5);
}
```

Example 3 (PNG heightmap) [Requires 2015.03]:

```openscad
// Example 3a
scale([1, 1, 0.1]) surface(file = "smiley.png", center = true);

// Example 3b (invert)
scale([1, 1, 0.1]) surface(file = "smiley.png", center = true, invert = true);
```

Example 4 (PNG heightmap) [Requires 2015.03]:

```openscad
surface(file = "BRGY-Grey.png", center = true, invert = false);
```

## search

The `search()` function finds occurrences of values or lists in a vector, string, or list-of-lists.

### Usage

```
search(match_value, string_or_vector [, num_returns_per_match [, index_col_num ] ]);
```

### Arguments

- `match_value`:
  - Single string: searches per-character in the second argument (string or list-of-lists). Does not search substrings.
  - Single number.
  - List of values: searches for each item in the list independently.
  - To search for the whole string/list as a single item, wrap in another list, e.g. `["abc"]` or `[[6,7,8]]`.
  - If boolean, returns `undef`.

- `string_or_vector`:
  - The string or list to search.
  - If `match_value` is a string, this should be a string (search per character) or a list-of-lists. For list-of-lists, only one index of each sublist is searched (see `index_col_num`).
  - If a character fails to match (with list-of-lists and `num_returns_per_match == 1`), a warning is printed and that result is excluded.

- `num_returns_per_match` (default 1):
  - If `> 1`, returns up to that many indices per match (list of lists).
  - If `0`, returns all matches per item (list of lists).
  - If `1`, returns first match per item (vector).

- `index_col_num` (default 0):
  - For list-of-lists, specifies which index of each sublist to search.

### Search usage examples

See example023.scad for a renderable example.

#### Index values returned as list

| # | Code                         | Result   |
|---|------------------------------|----------|
| 1 | `search("a","abcdabcd");`    | `[0]`    |
| 2 | `search("e","abcdabcd");`    | `[]`     |
| 3 | `search("a","abcdabcd",0);`  | `[[0,4]]`|

Example 4 (list-of-lists):

```openscad
data = [
    ["a",1],["b",2],["c",3],["d",4],
    ["a",5],["b",6],["c",7],["d",8],["e",9]
];
search("a", data, num_returns_per_match=0);  // -> [[0,4]]
```

#### Search on different column; return index values

```openscad
data = [
    ["a",1],["b",2],["c",3],["d",4],
    ["a",5],["b",6],["c",7],["d",8],["e",3]
];

echo(search(3, data)); // default searches index 0 -> []
echo(search(3, data, num_returns_per_match=0, index_col_num=1)); // -> [2, 8]

// Console:
// ECHO: []
// ECHO: [2, 8]
```

#### Search on list of values

Return all matches per search element (`num_returns_per_match = 0`):

```openscad
data = [
    ["a",1],["b",2],["c",3],["d",4],
    ["a",5],["b",6],["c",7],["d",8],["e",9]
];

search("abc", data, num_returns_per_match=0);
// Returns: [[0,4],[1,5],[2,6]]
```

Return first match per element (`num_returns_per_match = 1`):

```openscad
data = [
    ["a",1],["b",2],["c",3],["d",4],
    ["a",5],["b",6],["c",7],["d",8],["e",9]
];

search("abc", data, num_returns_per_match=1);
// Returns: [0,1,2]
```

Return first two matches per element:

```openscad
data = [
    ["a",1],["b",2],["c",3],["d",4],
    ["a",5],["b",6],["c",7],["d",8],["e",9]
];

search("abce", data, num_returns_per_match=2);
// Returns: [[0,4],[1,5],[2,6],[8]]
```

#### Search on list of strings

```openscad
lTable2 = [
    ["cat",1],["b",2],["c",3],["dog",4],["a",5],["b",6],["c",7],["d",8],
    ["e",9],["apple",10],["a",11]
];
lSearch2 = ["b","zzz","a","c","apple","dog"];
l2 = search(lSearch2, lTable2);
echo(str("Default list string search (",lSearch2,"): ", l2));

// Console:
// ECHO: "Default list string search (["b", "zzz", "a", "c", "apple", "dog"]): [1, [], 4, 2, 9, 3]"
```

#### Getting the right results

```openscad
// work out which vectors get the results
v = [["O",2],["p",3],["e",9],["n",4],["S",5],["C",6],["A",7],["D",8]];

// echo(v[0]);                 // -> ["O",2]
echo(v[1]);                    // -> ["p",3]
echo(v[1][0], v[1][1]);        // -> "p", 3

echo(search("p", v));          // find "p" -> [1]
echo(search("p", v)[0]);       // -> 1

echo(search(9, v, 0, 1));      // find 9 in column 1 -> [2]
echo(v[search(9, v, 0, 1)[0]]);    // -> ["e",9]
echo(v[search(9, v, 0, 1)[0]][0]); // -> "e"
echo(v[search(9, v, 0, 1)[0]][1]); // -> 9

echo(v[search("p", v, 1, 0)[0]][1]); // -> 3
echo(v[search("p", v, 1, 0)[0]][0]); // -> "p"
echo(v[search("d", v, 1, 0)[0]][0]); // "d" not found -> undef
echo(v[search("D", v, 1, 0)[0]][1]); // -> 8
```

## OpenSCAD version

- `version()` returns a vector `[year, month, day]`, e.g. `[2011, 9, 23]`.
- `version_num()` returns a numeric form, e.g. `20110923`.

## parent_module(n) and $parent_modules

- `$parent_modules` contains the number of modules in the instantiation stack.
- `parent_module(i)` returns the name of the module `i` levels above the current one in the instantiation stack (based on where modules are instantiated).

Example (useful for BOMs or diagnostics):

```openscad
module top() { children(); }
module middle() { children(); }

top()
    middle()
        echo(parent_module(0)); // prints "middle"

top()
    middle()
        echo(parent_module(1)); // prints "top"
```

## assert

[Note: Requires 2019.05]

Assert evaluates a logical expression. If false, preview/render stops and an error is reported with the expression and optional message.

Usage:

```openscad
assert(condition);
assert(condition, message);
```

Parameters:
- `condition`: expression to evaluate.
- `message`: optional string to output when the assertion fails.

### Example

```openscad
// assert_example1.scad
cube();
assert(false);
sphere();

// ERROR: Assertion 'false' failed in file assert_example1.scad, line 2
```

### Checking parameters

```openscad
module row(cnt = 3){
    // Count has to be a positive integer greater 0
    assert(cnt > 0);
    for (i = [1 : cnt]) {
        translate([i * 2, 0, 0]) sphere();
    }
}

row(0);
// ERROR: Assertion '(cnt > 0)' failed in file assert_example2.scad, line 3
```

### Adding message

```openscad
module row(cnt = 3){
    assert(cnt > 0, "Count has to be a positive integer greater 0");
    for (i = [1 : cnt]) {
        translate([i * 2, 0, 0]) sphere();
    }
}

row(0);
// ERROR: Assertion '(cnt > 0)': "Count has to be a positive integer greater 0" failed in file assert_example3.scad, line 2
```

### Using assertions in functions

`assert` returns its children; in a function, chain checks and then compute:

```openscad
function f(a, b) =
    assert(a < 0, "wrong a")       // assert input
    assert(b > 0, "wrong b")       // assert input
    let (c = a + b)                // derive a new value
    assert(c != 0, "wrong c")      // assert derived value
    a * b;                         // calculate
```

---

# En.Wikibooks.Org Wiki Openscad User Manual Type Test Functions Is Bool

# OpenSCAD User Manual — Type Test Functions

## is_undef

Note: Requires version 2019.05

- Accepts one parameter. Returns true if the argument is undef, otherwise false.
- When checking a variable like is_undef(a), the variable lookup is silent and does not produce warnings about unknown variables.

Example (causes warnings if not using is_undef):
```openscad
if (a == undef) {
  // code goes here
}

b = (a == undef) ? true : false;
```

Using is_undef with special variables:
```openscad
exploded = is_undef($exploded) ? 0 : $exploded; // 1 for exploded view
```

### Legacy support

For older OpenSCAD versions, is_undef can be emulated (will cause warnings):
```openscad
function is_undef(a) = (undef == a);
```

## is_list

Note: Requires version 2019.05

```openscad
echo("returning true");
echo(is_list([]));
echo(is_list([1]));
echo(is_list([1,2]));
echo(is_list([true]));
echo(is_list([1,2,[5,6],"test"]));

echo("--------");

echo("returning false");
echo(is_list(1));
echo(is_list(1/0));
echo(is_list(((1/0)/(1/0))));
echo(is_list("test"));
echo(is_list(true));
echo(is_list(false));

echo("--------");

echo("causing warnings:");
echo(is_list());
echo(is_list(1,2));
```

## is_num

Note: Requires version 2019.05

```openscad
echo("a number is a number:");
echo(is_num(0.1));
echo(is_num(1));
echo(is_num(10));

echo("inf is a number:");
echo(is_num(+1/0)); // +inf
echo(is_num(-1/0)); // -inf

echo("nan is not a number:");
echo(is_num(0/0));        // nan
echo(is_num((1/0)/(1/0))); // nan

echo("resulting in false:");
echo(is_num([]));
echo(is_num([1]));
echo(is_num("test"));
echo(is_num(false));
echo(is_num(undef));
```

## is_bool

Note: Requires version 2019.05

```openscad
echo("resulting in true:");
echo(is_bool(true));
echo(is_bool(false));

echo("resulting in false:");
echo(is_bool([]));
echo(is_bool([1]));
echo(is_bool("test"));
echo(is_bool(0.1));
echo(is_bool(1));
echo(is_bool(10));
echo(is_bool(0/0));           // nan
echo(is_bool((1/0)/(1/0)));   // nan
echo(is_bool(1/0));           // inf
echo(is_bool(-1/0));          // -inf
echo(is_bool(undef));
```

## is_string

Note: Requires version 2019.05

```openscad
echo("resulting in true:");
echo(is_string(""));
echo(is_string("test"));

echo("resulting in false:");
echo(is_string(0.1));
echo(is_string(1));
echo(is_string(10));
echo(is_string([]));
echo(is_string([1]));
echo(is_string(false));
echo(is_string(0/0));           // nan
echo(is_string((1/0)/(1/0)));   // nan
echo(is_string(1/0));           // inf
echo(is_string(-1/0));          // -inf
echo(is_string(undef));
```

## is_function

Note: Requires version 2021.01

- Works only for expressions. Can be applied to function literals or variables containing functions.
- Does not work with built-in functions or normal function definitions.

```openscad
echo(is_function(function(x) x*x)); // ECHO: true

func = function(x) x+x;
echo(is_function(func)); // ECHO: true

function f(x) = x;
echo(is_function(f)); // WARNING: Ignoring unknown variable 'f' / ECHO: false
```

## is_object

Note: Requires version Development snapshot

Returns true if the argument is an object, and false otherwise.

---

