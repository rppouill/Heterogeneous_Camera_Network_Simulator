#!/usr/bin/tclsh
# Use me as : vsim -do run_gui.tcl
proc compile_design {} {
  puts " \t >> Compiling project files ..."
  vlib work
  vmap work work
  vcom -2008 -work work test.vhd
  vcom -2008 -work work testbench.vhd
}

proc sim_design {} {
  puts " \t >> Performing RTL Sim ..."
  vsim -f args.txt work.testbench
  #set msp_lib /home/kamel/dev/etc/modelsim_utils
  #source $msp_lib/auto_wave.tcl
  source auto_wave.tcl
  run 2 ms
}

proc exit_sim  {} {
 quit -force
}

proc all {} {
  compile_design
  sim_design
}

all