#!/usr/bin/tclsh
# Use me as : vsim -do run_cli.tcl
# TODO
proc compile_design {} {
  puts " \t >> Compiling project files ..."
  vlib -unix <work placeholder>/work
  vmap <work placeholder>/work
  vcom -2008 -work <work placeholder>/work /home/ropouillard/Documents/Thesis_Working/Simulateur/First/test.vhd
  vcom -2008 -work <work placeholder>/work /home/ropouillard/Documents/Thesis_Working/Simulateur/First/testbench.vhd
}

proc sim_design {} {
  puts " \t >> Performing RTL Sim ..."
  #vsim work.testbench
  vsim -f <args placeholder> <work placeholder>/work.testbench
  vcd file <work placeholder>/results.vcd
  vcd add -r *
  run 5 ms
}

proc exit_sim  {} {
 quit -force
}

proc all {} {
  compile_design
  sim_design

}

all