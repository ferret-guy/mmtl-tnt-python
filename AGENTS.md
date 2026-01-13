# Repository guidance

## Where to find build/install/run instructions

- `README` includes the Ubuntu/Debian dependency list, bootstrap steps, build commands,
  the required impedance test, and the install command.
- `INSTALL` contains the same step-by-step build, required test, and install guidance
  for people reading the traditional install document.

## Required impedance test

Run the BEM test driver to validate impedance output:

  wish bem/tests/test_bem.tcl

The test writes a log to `bem/tests/test_bem.log`, and the example impedance
output referenced by the docs is stored in `bem/tests/test1.result`.
