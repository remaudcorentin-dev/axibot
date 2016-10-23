MAX_RETRIES = 100

# These are unitless timing values used by the EBB.
SERVO_MIN = 7500
SERVO_MAX = 28000

SERVO_SPEED = 50
EXTRA_PEN_UP_DELAY = 400
EXTRA_PEN_DOWN_DELAY = 400
SMOOTHNESS = 2.0

SPEED_SCALE = 24950

# Seconds of acceleration to reach full speed with pen down.
ACCEL_TIME_PEN_DOWN = 0.25
SPEED_PEN_DOWN = 0.25 * SPEED_SCALE

# Seconds of acceleration to reach full speed with pen up.
#ACCEL_TIME_PEN_UP = 1.0
ACCEL_TIME_PEN_UP = 2.0
SPEED_PEN_UP = 0.75 * SPEED_SCALE

# Short-move pen-up distance threshold in inches, below which we use the faster
# pen-down acceleration rate.
SHORT_THRESHOLD = 1.0

# Motor steps per inch in 16X microstepping mode.
DPI_16X = 2032

# Time interval in seconds to update motor control.
TIME_SLICE = 0.030

# Corner rounding/tolerance factor.
CORNERING = 2.0
