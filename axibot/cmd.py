from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging

import sys
import argparse
from datetime import timedelta

from . import svg, planning, moves, config
from .ebb import EiBotBoard


def manual_command(bot, cmd):
    args = cmd.split()
    method = args[0]
    arg = args[1:]
    arg = tuple(map(int, arg))
    try:
        getattr(bot, method)(*arg)
    except AttributeError as e:
        print("Command not found: %s" % method)
    except (TypeError, ValueError) as e:
        print("Error: %s" % e)


def manual(opts):
    bot = EiBotBoard.find()
    try:
        pen_down_position = 45
        pen_up_position = 75
        bot.servo_setup(pen_down_position, pen_up_position,
                        config.SERVO_SPEED, config.SERVO_SPEED)
        if opts.cmd:
            cmd = ' '.join(opts.cmd)
            manual_command(bot, cmd)
        else:
            while True:
                cmd = input('(axibot) ')
                manual_command(bot, cmd)
    finally:
        bot.close()


def file_to_actions(filename, pen_up_delay, pen_down_delay):
    paths = svg.extract_paths(filename)
    segments = svg.plan_segments(paths, smoothness=100)
    transits = svg.add_pen_transits(segments)
    step_transits = planning.convert_inches_to_steps(transits)
    segments_limits = planning.plan_velocity(step_transits)
    actions = planning.plan_actions(segments_limits,
                                    pen_up_delay=pen_up_delay,
                                    pen_down_delay=pen_down_delay)
    return actions


def human_friendly_timedelta(td):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    pieces = []
    if days:
        pieces.append(("%d days" % days) if days > 1 else "1 day")
    if hours:
        pieces.append(("%d hours" % hours) if hours > 1 else "1 hour")
    if minutes:
        pieces.append(("%d minutes" % minutes) if minutes > 1 else "1 minute")
    if seconds:
        pieces.append(("%d seconds" % seconds) if seconds > 1 else "1 second")
    return ", ".join(pieces)


def info(opts):
    print("Loading %s..." % opts.filename)

    # XXX find pen positions with user interaction?
    pen_up_position = 75
    pen_down_position = 45
    # XXX better parameter config
    smoothness = 100

    pen_up_delay, pen_down_delay = \
        moves.calculate_pen_delays(pen_up_position, pen_down_position)

    actions = file_to_actions(opts.filename, pen_up_delay, pen_down_delay)
    duration_ms = sum(action.time() for action in actions)
    td = timedelta(seconds=(duration_ms / 1000))
    print("Number of moves: %s" % len(actions))
    print("Expected time: %s" % human_friendly_timedelta(td))


def plot(opts):
    print("Loading %s..." % opts.filename)

    # XXX find pen positions with user interaction?
    pen_up_position = 75
    pen_down_position = 45
    # XXX better parameter config
    smoothness = 100

    pen_up_delay, pen_down_delay = \
        moves.calculate_pen_delays(pen_up_position, pen_down_position)

    actions = file_to_actions(opts.filename, pen_up_delay, pen_down_delay)
    count = len(actions)
    print("Calculated %d actions." % count)

    bot = EiBotBoard.find()
    try:
        bot.pen_up(1000)
        print("Configuring servos.")
        bot.disable_motors()
        bot.servo_setup(pen_down_position, pen_up_position,
                        config.SERVO_SPEED, config.SERVO_SPEED)
        print("Pen up and motors off. Move carriage to top left corner.")
        input("Press enter to begin.")

        bot.enable_motors(1)

        for ii, move in enumerate(actions):
            print("Move %d/%d: %s" % (ii, count, move))
            bot.do(move)

        bot.pen_up(1000)
        print("Finished!")
    finally:
        bot.close()


def server(opts):
    from axibot.server import serve
    serve(opts)


def main(args=sys.argv):
    p = argparse.ArgumentParser(description='Print with the AxiDraw.')
    p.add_argument('--verbose', action='store_true')
    p.set_defaults(function=None)

    subparsers = p.add_subparsers(help='sub-command help')

    p_plot = subparsers.add_parser(
        'plot', help='Plot an SVG file directly.')
    p_plot.add_argument('filename')
    p_plot.set_defaults(function=plot)

    p_info = subparsers.add_parser(
        'info', help='Print information about an SVG file.')
    p_info.add_argument('filename')
    p_info.set_defaults(function=info)

    p_server = subparsers.add_parser(
        'server', help='Run a server for remote plotting.')
    p_server.add_argument('--port', type=int, default=8888)
    p_server.set_defaults(function=server)

    p_manual = subparsers.add_parser(
        'manual', help='Manual control shell.')
    p_manual.add_argument('cmd', nargs='*')
    p_manual.set_defaults(function=manual)

    opts, args = p.parse_known_args(args[1:])

    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO)

    if opts.function:
        return opts.function(opts)
    else:
        p.print_help()
