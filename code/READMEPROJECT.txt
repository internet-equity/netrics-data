Essentially my dataframe is a singular device that is recording the max, min, avg, and mdev latency every 5 minutes for the month of october.
I further broke down the dataset into subsets to make it easier for analysis, exploration and to meet objectves.(subsets include: All rows including atlanta, then further broke down into different subsets for each type [max,min,avg,mdev], then focused on the max type dataframe,then further broke that down into subsets of 7 different days that I randomly sampled.
Made time series plots of each day to help determine anomaly threshold
Created function to pull into entire dataframe to detected anomaly values and add it to a column, and then sum up all anomaly’s for each day in the month
