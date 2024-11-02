me=usec
        Maximum amount of time ext4 should wait for additional filesystem
        operations to be batch together with a synchronous write operation.
        Since a synchronous write operation is going to force a commit and then
        a wait for the I/O complete, it doesn't cost much, and can be a huge
        throughput win, we wait for a small amount of time to see if any other
        transactions can piggyback on the synchronous write.   The algorithm
        used is designed to automatically tune for the speed of the disk, by
        measuring the amount of time (on average) that it takes to finish
        committing a transaction.  Call this time the "commit time".  If the
        time that the transaction has been running is less than the commit
        time, ext4 will try sleeping for the commit time to see if other
        operations will join the transaction.   The commit time is capped by
        the max_batch_time, which defaults to 15000us (15ms).   This
        optimization can be turned off entirely by setting max_batch_time to 0.

  min_batch_time=usec
        This parameter sets the commit time (as described above) to be at least
        min_batch_time.  It defaults to zero microseconds.  Increasing this
        parameter may improve the throughput of multi-threaded, synchronous
    