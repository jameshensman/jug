# -*- coding: utf-8 -*-
# Copyright (C) 2008  Murphy Lab
# Carnegie Mellon University
# 
# Written by Luís Pedro Coelho <lpc@cmu.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# For additional information visit http://murphylab.web.cmu.edu or
# send email to murphy@cmu.edu

from __future__ import division

from collections import defaultdict
from time import sleep
from store import create_directories
import sys
import random
import options
import task
import jugfile

def do_print():
    '''
    do_print()

    Print a count of task names.
    '''
    task_counts = defaultdict(int)
    for t in task.alltasks:
        task_counts[t.name] += 1
    for tnc in task_counts.items():
        print 'Task %s: %s' % tnc

task_names = set(t.name for t in task.alltasks)
tasks = task.alltasks
def execute():
    '''
    execute()

    Implement 'execute' command
    '''
    tasks_executed = defaultdict(int)
    tasks_loaded = defaultdict(int)
    if options.shuffle:
        random.shuffle(tasks)
    task.topological_sort(tasks)
    for t in tasks:
        if not t.can_run():
            waits = [4,8,16,32,64,128,128,128,128,1024,2048]
            for w in waits:
                print 'waiting...', w, 'for', t.name
                sleep(w)
                if t.can_run(): break
            if not t.can_run(): # This was about an hour wait
                print 'No tasks can be run!'
                return
        locked = t.lock()
        try:
            if t.can_load():
                t.load()
                tasks_loaded[t.name] += 1
            elif locked:
                t.run()
                tasks_executed[t.name] += 1
        finally:
            if locked: t.unlock()

    print '%-20s%12s%12s' %('Task name','Executed','Loaded')
    print ('-' * (20+12+12))
    for t in task_names:
        print '%-20s%12s%12s' % (t,tasks_executed[t],tasks_loaded[t])

def status():
    '''
    status()

    Implements the status command.
    '''
    tasks_ready = defaultdict(int)
    tasks_finished = defaultdict(int)
    tasks_running = defaultdict(int)
    tasks_waiting = defaultdict(int)
    changed = True
    while changed:
        changed = False
        for t in tasks:
            if not t.finished and t.can_load():
                tasks_finished[t.name] += 1
                t.load()
                changed = True
    for t in tasks:
        if not t.finished:
            if t.can_run():
                if t.is_locked():
                    tasks_running[t.name] += 1
                else:
                    tasks_ready[t.name] += 1
            else:
                tasks_waiting[t.name] += 1

    print '%-20s%12s%12s%12s%12s' %('Task name','Waiting','Ready','Finished','Running')
    print ('-' * (20+12+12+12+12))
    for t in task_names:
        print '%-20s%12s%12s%12s%12s' % (t,tasks_waiting[t],tasks_ready[t],tasks_finished[t],tasks_running[t])
    print

def init():
    '''
    init()

    Initializes jug (creates needed directories &c).
    '''
    create_directories(options.tempdir)

def main():
    options.parse()
    init()
    if options.cmd == 'execute':
        execute()
    elif options.cmd == 'count':
        do_print()
    elif options.cmd == 'status':
        status()
    else:
        print >>sys.stderr, 'Unknown command: \'%s\'' % options.cmd

if __name__ == '__main__':
    main()

# vim: set ts=4 sts=4 sw=4 expandtab smartindent: