# Project Overview
This project will execute some jobs (ddls/dmls) over a database server asynchronously.


# Requirements
- Flask framework must use
- Command line interface must be used
- Command line arguments must be used
- Config file must be used for database server connection and other parameters
- Log method can be changeable via arguments (console, log file, etc.), default log method must be defined in config file
- Jobs should be able to be run asynchronously
- OOP approach must be used
- Comments must be added to each element
- 'Keep it Simple' approach must be used


# What Will To Do
- There will be a jobs table on database server, this table can be created with command line argument
- A job can be added with command line arguments (May be read different sources: argument/file/etc...)
- Job list can be get with command line arguments 
- A job's status can be changed as ignore via command line argument
- A job can be deleted via command line argument
- A job can start/stop via command line argument
- Job's state must be checked for desired operation
- A log item must be added to defined or given log method for each command's result
