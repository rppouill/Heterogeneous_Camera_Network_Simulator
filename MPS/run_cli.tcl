#!/usr/bin/tclsh
# Use me as : vsim -do run_cli.tcl
# TODO
proc compile_design {} {
  puts " \t >> Compiling project files ..."
  vlib work
  vmap work work
  vcom -2008 -work work ./ModelSim/test.vhd
  vcom -2008 -work work ./ModelSim/testbench.vhd
}

proc sim_design {} {
  puts " \t >> Performing RTL Sim ..."
  #vsim work.testbench
  vsim -f args.txt work.testbench
  vcd file results.vcd
  vcd add -r *
  run 20 ms
}

proc exit_sim  {} {
 quit -force
}

proc all {} {
  compile_design
  sim_design
  exit_sim
}

all