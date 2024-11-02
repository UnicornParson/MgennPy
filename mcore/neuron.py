ot be used until they are
initialized, which does not happen until some time after the scheduler
spawns the first task. Given that there are parts of the kernel that
really do want to execute grace periods during this mid-boot “dead
zone”, expedited grace periods must do something else during this time.

What they do is to fall back to the old practice of requiring that the
requesting task drive the expedited grace period, as was the case before
the use of workqueues. However, the requesting task is only required to
drive the grace period during the mid-boot dead zone. Before mid-boot, a
synchronous grace period is a no-op. Some time after mid-boot,
workqueues are used.

Non-expedited non-SRCU synchronous grace periods must also operate
normally during mid-boot. This is handled by causing non-expedited grace
periods to take the expedited code path during mid-boot.

The current code assumes that there are no POSIX signals during the
mid-boot dead zone. However, if an overwhelming need for POSIX signals
somehow arises, appropriate adjustments can be made to the expedited
stall-warning code. One such adjustment would reinstate the
pre-workqueue stall-warning checks, but only during the mid-boot dead
zone.

With this refinement, synchronous grace periods can now be used from
task context pretty much any time during the life of the kernel. That
is, aside from some points in the suspend, hibernate, or shutdown code
path.

Summary
~~~~~~~

Expedited grace periods use a sequence-number approach to promote
batching, so that a single grace-period operation can serve numerous
requests. A funnel lock is used to efficiently identify the one task out
of a concurrent group that will request the grace period. All members of
the group w