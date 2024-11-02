.. SPDX-License-Identifier: GPL-2.0

========================
ext4 General Information
========================

Ext4 is an advanced level of the ext3 filesystem which incorporates
scalability and reliability enhancements for supporting large filesystems
(64 bit) in keeping with increasing disk capacities and state-of-the-art
feature requirements.

Mailing list:	linux-ext4@vger.kernel.org
Web site:	http://ext4.wiki.kernel.org


Quick usage instructions
========================

Note: More extensive information for getting started with ext4 can be
found at the ext4 wiki site at the URL:
http://ext4.wiki.kernel.org/index.php/Ext4_Howto

  - The latest version of e2fsprogs can be found at:

    https://www.kernel.org/pub/linux/kernel/people/tytso/e2fsprogs/

	or

    http://sourceforge.net/project/showfiles.php?group_id=2406

	or grab the latest git repository from:

   https://git.kernel.org/pub/scm/fs/ext2/e2fsprogs.git

  - Create a new filesystem using the ext4 filesystem type:

        # mke2fs -t ext4 /dev/hda1

    Or to configure an existing ext3 filesystem to support extents:

	# tune2fs -O extents /dev/hda1

    If the filesystem was created with 128 byte inodes, it can be
    converted to use 256 byte for greater efficiency via:

        # tune2fs -I 256 /dev/hda1

  - Mounting:

	# mount -t ext4 /dev/hda1 /wherever

  - When comparing performance with other filesystems, it's always
    important to try multiple workloads; very often a subtle change in a
    workload parameter can completely change the ranking of which
    filesystems do well compared to others.  When comparing versus ext3,
    note that ext4 enables write barriers by default, while ext3 does
    not enable write barriers by default.  So it is useful to use
    explicitly specify whether barriers are enabled or not when via the
    '-o barriers=[0|1]' mount option for both ext3 and ext4 filesystems
    for a fair comparison.  When tuning ext3 for best benchmark numbers,
    it is often worthwhile to try changing the data journaling mode; '-o
    data=writeback' can be faster for some workloads.  (Note however that
    running mounted with data=writeback can potentially leave stale data
    exposed in recently written files in case of an unclean shutdown,
    which could be a security exposure in some situations.)  Configuring
    the filesys