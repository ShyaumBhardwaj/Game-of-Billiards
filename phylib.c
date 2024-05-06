
#include "phylib.h"

//================================================================Part 1================================================================

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos)
{
    phylib_object *object = (phylib_object *)malloc(sizeof(phylib_object));
    if (object != NULL)
    {
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = number;
        object->obj.still_ball.pos = *pos;
    }
    return object;
}

phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc)
{
    phylib_object *object = (phylib_object *)malloc(sizeof(phylib_object));
    if (object != NULL)
    {
        object->type = PHYLIB_ROLLING_BALL;
        object->obj.rolling_ball.number = number;
        object->obj.rolling_ball.pos = *pos;
        object->obj.rolling_ball.vel = *vel;
        object->obj.rolling_ball.acc = *acc;
    }
    return object;
}

phylib_object *phylib_new_hole(phylib_coord *pos)
{
    phylib_object *object = (phylib_object *)malloc(sizeof(phylib_object));
    if (object)
    {
        object->type = PHYLIB_HOLE;
        object->obj.hole.pos = *pos;
    }
    return object;
}

phylib_object *phylib_new_hcushion(double y)
{
    phylib_object *object = (phylib_object *)malloc(sizeof(phylib_object));
    if (object)
    {
        object->type = PHYLIB_HCUSHION;
        object->obj.hcushion.y = y;
    }
    return object;
}

phylib_object *phylib_new_vcushion(double x)
{
    phylib_object *object = (phylib_object *)malloc(sizeof(phylib_object));
    if (object)
    {
        object->type = PHYLIB_VCUSHION;
        object->obj.vcushion.x = x;
    }
    return object;
}

phylib_table *phylib_new_table(void)
{
    phylib_table *bill_table = (phylib_table *)malloc(sizeof(phylib_table));
    if (bill_table)
    {
        bill_table->time = 0.0;

        bill_table->object[0] = phylib_new_hcushion(0.0);
        bill_table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
        bill_table->object[2] = phylib_new_vcushion(0.0);
        bill_table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);
        bill_table->object[4] = phylib_new_hole(&(phylib_coord){0.0, 0.0});                                       // bottom-left hole
        bill_table->object[5] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_WIDTH});                        // Bottom-left hole
        bill_table->object[6] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_LENGTH});                       // Top-right hole
        bill_table->object[7] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, 0.0});                        // Bottom-right hole
        bill_table->object[8] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_LENGTH / 2.0, PHYLIB_TABLE_WIDTH});  // Mid-top hole
        bill_table->object[9] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_LENGTH / 2.0, PHYLIB_TABLE_LENGTH}); // Mid-bottom hole

        // Set remaining pointers to NULL for all the balls to be added later
        for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i)
        {
            bill_table->object[i] = NULL;
        }
    }
    return bill_table;
}
//----------------------------------------------------------------Part 2================================================

void phylib_copy_object(phylib_object **dest, phylib_object **src)
{
    if (*src != NULL)
    {
        *dest = (phylib_object *)malloc(sizeof(phylib_object));
        if (*dest != NULL)
        {
            memcpy(*dest, *src, sizeof(phylib_object));
        }
    }
}

phylib_table *phylib_copy_table(phylib_table *table)
{
    if (table == NULL)
    {
        return NULL;
    }

    // Allocate memory for new table
    phylib_table *table_new = (phylib_table *)malloc(sizeof(phylib_table));
    if (table_new == NULL)
    {
        return NULL; // Memory allocation failed
    }

    // Copy old table to new one
    memcpy(table_new, table, sizeof(phylib_table));

    // Copy each object of the table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        if (table->object[i] != NULL)
        {
            // Allocating memory for a new object
            table_new->object[i] = (phylib_object *)malloc(sizeof(phylib_object));
            if (table_new->object[i] == NULL)
            {
                for (int j = 0; j < i; ++j)
                {
                    free(table_new->object[j]);
                }
                free(table_new);
                return NULL;
            }
            // memcpy old object data in new
            memcpy(table_new->object[i], table->object[i], sizeof(phylib_object));
        }
    }

    return table_new;
}

void phylib_add_object(phylib_table *table, phylib_object *object)
{
    if (table == NULL || object == NULL)
    {
        return;
    }
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        if (table->object[i] == NULL)
        {
            table->object[i] = object; // add the object in the array
            break;
        }
    }
}

void phylib_free_table(phylib_table *table)
{
    if (table != NULL)
    {
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i) // start with only balls hence 10
        {
            if (table->object[i] != NULL)
            {
                free(table->object[i]); // Free memory for each object on the table
                table->object[i] = NULL;
            }
        }
        free(table);
    }
}

phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2)
{
    phylib_coord sub;
    sub.x = c1.x - c2.x;
    sub.y = c1.y - c2.y;
    return sub;
}

double phylib_length(phylib_coord c)
{
    // Using Pythagorean theorem
    return sqrt(c.x * c.x + c.y * c.y);
}

double phylib_dot_product(phylib_coord a, phylib_coord b)
{
    return a.x * b.x + a.y * b.y;
}

double phylib_distance(phylib_object *obj1, phylib_object *obj2)
{
    // Check if obj1 is a PHYLIB_ROLLING_BALL
    if (obj1->type != PHYLIB_ROLLING_BALL)
    {
        return -1.0;
    }

    // Calculate the distance based on the type of obj2
    double distance = -1.0; // Default value if obj2 is not a valid type

    switch (obj2->type)
    {
    case PHYLIB_STILL_BALL:

    {
        distance = phylib_length(phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.still_ball.pos)) - PHYLIB_BALL_DIAMETER;
        break;
    }
    case PHYLIB_ROLLING_BALL:
    {
        distance = phylib_length(phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.rolling_ball.pos)) - PHYLIB_BALL_DIAMETER;
        break;
    }
    case PHYLIB_HOLE:
    {
        distance = phylib_length(phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.hole.pos)) - PHYLIB_HOLE_RADIUS;

        break;
    }
    case PHYLIB_HCUSHION:
    {
        distance = fabs(obj1->obj.rolling_ball.pos.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
        break;
    }
    case PHYLIB_VCUSHION:
    {
        distance = fabs(obj1->obj.rolling_ball.pos.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
        break;
    }
    default:
        // Return -1.0 for any other type of obj2
        break;
    }

    return distance;
}

//============================================================================Part 3 =================================================================

void phylib_roll(phylib_object *new, phylib_object *old, double time)
{
    if (new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL)
    {
        return; // Do nothing if not PHYLIB_ROLLING_BALLs
    }

    new->obj.rolling_ball.pos.x = old->obj.rolling_ball.pos.x + old->obj.rolling_ball.vel.x *time + 0.5 * old->obj.rolling_ball.acc.x *time *time;
    new->obj.rolling_ball.pos.y = old->obj.rolling_ball.pos.y + old->obj.rolling_ball.vel.y *time + 0.5 * old->obj.rolling_ball.acc.y *time *time;

    new->obj.rolling_ball.vel.x = old->obj.rolling_ball.vel.x + old->obj.rolling_ball.acc.x *time;
    new->obj.rolling_ball.vel.y = old->obj.rolling_ball.vel.y + old->obj.rolling_ball.acc.y *time;

    if ((old->obj.rolling_ball.vel.x * new->obj.rolling_ball.vel.x) < 0.0)
    {
        new->obj.rolling_ball.vel.x = 0.0;
        new->obj.rolling_ball.acc.x = 0.0;
    }

    if ((old->obj.rolling_ball.vel.y * new->obj.rolling_ball.vel.y) < 0.0)
    {
        new->obj.rolling_ball.vel.y = 0.0;
        new->obj.rolling_ball.acc.y = 0.0;
    }
}

unsigned char phylib_stopped(phylib_object *object)
{

    double velocity = phylib_length(object->obj.rolling_ball.vel);
    if (velocity < PHYLIB_VEL_EPSILON)
    {
        // Convert to STILL_BALL
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos = object->obj.rolling_ball.pos;

        return 1; // Ball has stopped and been changes to a STILL_BALL
    }

    return 0; // Ball is still rolling
}

void phylib_bounce(phylib_object **a, phylib_object **b)
{
    if (!a || !b || !(*a) || !(*b) || (*a)->type != PHYLIB_ROLLING_BALL)
    {
        return; // Do nothing if invalid input or not PHYLIB_ROLLING_BALL
    }

    phylib_object *obj_a = *a;
    phylib_object *obj_b = *b;

    switch (obj_b->type)
    {
    case PHYLIB_HCUSHION:
        obj_a->obj.rolling_ball.vel.y = -obj_a->obj.rolling_ball.vel.y; // bounce mirroring speed for all
        obj_a->obj.rolling_ball.acc.y = -obj_a->obj.rolling_ball.acc.y;
        break;
    case PHYLIB_VCUSHION:
        obj_a->obj.rolling_ball.vel.x = -obj_a->obj.rolling_ball.vel.x;
        obj_a->obj.rolling_ball.acc.x = -obj_a->obj.rolling_ball.acc.x;
        break;
    case PHYLIB_HOLE:

        free(*a);
        *a = NULL;

        break;
    case PHYLIB_STILL_BALL:
        // change still ball to rolling ball and give it all the values initializing
        obj_b->type = PHYLIB_ROLLING_BALL;
        obj_b->obj.rolling_ball.pos = obj_b->obj.still_ball.pos;
        obj_b->obj.rolling_ball.acc.x = 0.0;
        obj_b->obj.rolling_ball.acc.y = 0.0; // initializing
        obj_b->obj.rolling_ball.vel.x = 0.0;
        obj_b->obj.rolling_ball.vel.y = 0.0;

    case PHYLIB_ROLLING_BALL:
    {
        // Calculate relative position and velocity by just making b as refernece
        phylib_coord r_ab = phylib_sub(obj_a->obj.rolling_ball.pos, obj_b->obj.rolling_ball.pos);

        phylib_coord v_rel = phylib_sub(obj_a->obj.rolling_ball.vel, obj_b->obj.rolling_ball.vel);

        // Calculate normal vector as in file
        double r_ab_length = phylib_length(r_ab);

        phylib_coord n = {r_ab.x / r_ab_length, r_ab.y / r_ab_length};

        // Calculate v_rel_n as in file
        double v_rel_n = phylib_dot_product(v_rel, n);

        // using the normal vector calculating velocities for both objects in both axises
        obj_a->obj.rolling_ball.vel.x = obj_a->obj.rolling_ball.vel.x - (v_rel_n * n.x);

        obj_a->obj.rolling_ball.vel.y = obj_a->obj.rolling_ball.vel.y - (v_rel_n * n.y);

        obj_b->obj.rolling_ball.vel.x = obj_b->obj.rolling_ball.vel.x + (v_rel_n * n.x);

        obj_b->obj.rolling_ball.vel.y = obj_b->obj.rolling_ball.vel.y + (v_rel_n * n.y);

        // calculating the total vector speed of both objects
        double speed_a = phylib_length(obj_a->obj.rolling_ball.vel);

        double speed_b = phylib_length(obj_b->obj.rolling_ball.vel);

        // applying drag as mentioned in file
        if (speed_a > PHYLIB_VEL_EPSILON)
        {
            obj_a->obj.rolling_ball.acc.x = ((-obj_a->obj.rolling_ball.vel.x) / speed_a) * PHYLIB_DRAG;

            obj_a->obj.rolling_ball.acc.y = ((-obj_a->obj.rolling_ball.vel.y) / speed_a) * PHYLIB_DRAG;
        }

        if (speed_b > PHYLIB_VEL_EPSILON)
        {
            obj_b->obj.rolling_ball.acc.x = ((-obj_b->obj.rolling_ball.vel.x) / speed_b) * PHYLIB_DRAG;

            obj_b->obj.rolling_ball.acc.y = ((-obj_b->obj.rolling_ball.vel.y) / speed_b) * PHYLIB_DRAG;
        }
        break;
    }
    default:
        break;
    }
}

unsigned char phylib_rolling(phylib_table *t)
{
    unsigned char rollingCount = 0;

    // Iterate through the ball objects on the table
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        // Check if object is a rolling ball
        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL)
        {
            rollingCount++; // increment the no of balls
        }
    }

    return rollingCount;
}

phylib_table *phylib_segment(phylib_table *table)
{
    phylib_table *copy_table = phylib_copy_table(table);
    unsigned char roll_balls;
    roll_balls = phylib_rolling(copy_table);
    double time = PHYLIB_SIM_RATE;
    if (roll_balls > 0)
    {

        while (time <= PHYLIB_MAX_TIME)
        {
            for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i)
            {
                if (copy_table->object[i] != NULL && copy_table->object[i]->type == PHYLIB_ROLLING_BALL)
                {
                    phylib_roll(copy_table->object[i], table->object[i], time);
                }
            }

            for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i)
            {

                if (copy_table->object[i] != NULL && copy_table->object[i]->type == PHYLIB_ROLLING_BALL && phylib_stopped(copy_table->object[i]))
                {
                    return copy_table; // stop while loop
                }

                for (int j = 0; j < PHYLIB_MAX_OBJECTS; ++j)
                {
                    if (i != j && copy_table->object[i] != NULL && copy_table->object[i]->type == PHYLIB_ROLLING_BALL && copy_table->object[j] != NULL && phylib_distance(copy_table->object[i], copy_table->object[j]) < 0.0)
                    {
                        phylib_bounce(&copy_table->object[i], &copy_table->object[j]);
                        return copy_table;
                    }
                }
            }

            time += PHYLIB_SIM_RATE;
            copy_table->time += PHYLIB_SIM_RATE;
        }

    }
    free(copy_table);
    return NULL;
}
//============================================================================A 2 =================================================================

char *phylib_object_string(phylib_object *object)
{
    static char string[80];
    if (object == NULL)
    {
        snprintf(string, 80, "NULL;");
        return string;
    }
    switch (object->type)
    {
    case PHYLIB_STILL_BALL:
        snprintf(string, 80,
                 "STILL_BALL (%d,%6.1lf,%6.1lf)",
                 object->obj.still_ball.number,
                 object->obj.still_ball.pos.x,
                 object->obj.still_ball.pos.y);
        break;
    case PHYLIB_ROLLING_BALL:
        snprintf(string, 80,
                 "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                 object->obj.rolling_ball.number,
                 object->obj.rolling_ball.pos.x,
                 object->obj.rolling_ball.pos.y,
                 object->obj.rolling_ball.vel.x,
                 object->obj.rolling_ball.vel.y,
                 object->obj.rolling_ball.acc.x,
                 object->obj.rolling_ball.acc.y);
        break;
    case PHYLIB_HOLE:
        snprintf(string, 80,
                 "HOLE (%6.1lf,%6.1lf)",
                 object->obj.hole.pos.x,
                 object->obj.hole.pos.y);
        break;
    case PHYLIB_HCUSHION:
        snprintf(string, 80,
                 "HCUSHION (%6.1lf)",
                 object->obj.hcushion.y);
        break;
    case PHYLIB_VCUSHION:
        snprintf(string, 80,
                 "VCUSHION (%6.1lf)",
                 object->obj.vcushion.x);
        break;
    }
    return string;
}
