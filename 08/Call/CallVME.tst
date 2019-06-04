// Test file for Call test.
//
// This test assumes NO BOOTSTRAP CODE is present.

load Call.vm,
output-file Call.out,
compare-to Call.cmp,
output-list RAM[0]%D1.6.1 
			RAM[1]%D1.6.1
			RAM[2]%D1.6.1
			RAM[3]%D1.6.1
			RAM[4]%D1.6.1;

set sp 256,
set local 300,
set argument 400,
set this 3000,
set that 4000;

repeat 50 {
  vmstep;
}
output;
output-list RAM[256]%D1.6.1 
			RAM[257]%D1.6.1
			RAM[258]%D1.6.1
			RAM[259]%D1.6.1
			RAM[260]%D1.6.1
			RAM[261]%D1.6.1
			RAM[262]%D1.6.1;
output;