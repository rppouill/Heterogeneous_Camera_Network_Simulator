LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
USE IEEE.STD_LOGIC_ARITH.ALL;
USE IEEE.STD_LOGIC_UNSIGNED.ALL;
USE IEEE.NUMERIC_STD.ALL;

library std;
use std.textio.all;


ENTITY TESTBENCH IS
	generic(
		IMG_FILENAME_IN  : string := "img/bw.hex";
		IMG_FILENAME_OUT : string := "img/bw_out.hex"
	);
END TESTBENCH;

ARCHITECTURE BEHAVIOR OF TESTBENCH IS 

	SIGNAL 	clk_in 		 : STD_LOGIC := '0';
	SIGNAL 	clk_out 		 : STD_LOGIC := '0';
	SIGNAL	 data_in     : STD_LOGIC_VECTOR(15 DOWNTO 0) := (others => '0');
	SIGNAL	 data_out    : STD_LOGIC_VECTOR(15 DOWNTO 0) := (others => '0');

	SIGNAL STOP : BOOLEAN := FALSE;

	--file FILENAME_IN: text is in "img/black.jpg";
	file pixel_i_file: text;
	file pixel_o_file: text;
	
	CONSTANT clk_period	:	time := 5ns;
	
	COMPONENT TEST
	PORT(
		clk_in      : IN STD_LOGIC;
		clk_out     : OUT STD_LOGIC;
		data_in     : IN STD_LOGIC_VECTOR(15 DOWNTO 0);
		data_out    : OUT STD_LOGIC_VECTOR(15 DOWNTO 0)
	);
	END COMPONENT TEST;
 
BEGIN
	test_INST: TEST
		port map(
			clk_in	=>	clk_in,
			clk_out	=>	clk_out,
			data_in	=> data_in,
			data_out	=> data_out
		);
	
	CLK_STIM : process
	begin
		clk_in <= '0';
		wait for clk_period;
		clk_in <= '1';
		wait for clk_period;
	end process;
	
	pixel_i_process: process
	variable in_line : line;
	variable pixel_from_file : std_logic_vector(15 downto 0);
	BEGIN		
		file_open(pixel_i_file,IMG_FILENAME_IN,read_mode);
		report " >> Pixel_i Stream: Generating..." severity note;
		while not endfile(pixel_i_file) loop
			wait until rising_edge(clk_in);
			readline(pixel_i_file, in_line);
			hread(in_line, pixel_from_file);
			data_in <= pixel_from_file;
		end loop;
		wait until rising_edge(clk_in);
		file_close(pixel_i_file);
		STOP <= TRUE;
		report "Test Completed !";
		wait;

	END PROCESS;

	pixel_o_process: process
	variable out_line : line;
	BEGIN
		file_open(pixel_o_file,IMG_FILENAME_OUT,write_mode);
		report " >> Pixel_o Stream: Generating..." severity note;
		wait until rising_edge(clk_in);
		loop
			wait until rising_edge(clk_in);
			if STOP then
				exit;
			end if;
			hwrite(out_line, data_out);
			writeline(pixel_o_file, out_line);
		end loop;
		file_close(pixel_o_file);
		wait;
	END PROCESS;

END BEHAVIOR;
	
	
	
	 