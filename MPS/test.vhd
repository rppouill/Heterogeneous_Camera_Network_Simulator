LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
USE IEEE.STD_LOGIC_ARITH.ALL;
USE IEEE.STD_LOGIC_UNSIGNED.ALL;
USE IEEE.NUMERIC_STD.ALL;


ENTITY test IS
PORT(
    clk_in      : IN STD_LOGIC;
    clk_out     : OUT STD_LOGIC;
    data_in     : IN STD_LOGIC_VECTOR(15 DOWNTO 0);
    data_out    : OUT STD_LOGIC_VECTOR(15 DOWNTO 0)
);
END test;


ARCHITECTURE rtl OF test IS

BEGIN 
    output: PROCESS(clk_in)
    BEGIN
        IF (clk_in'EVENT AND clk_in = '1') THEN
            data_out <= data_in;
        END IF;
    END PROCESS output;



    clk_out <= not(clk_in);
    

END rtl;
