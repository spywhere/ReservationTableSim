import random
import time
import uuid

try:
    input = raw_input
except:
    pass


################################################################################

simulation_speed = 0.1

food_shops = [
    {
        "name": "Drink",
        "serving_time": 1,
        "eating_time": [3, 4]
    }, {
        "name": "Rice",
        "serving_time": 2,
        "eating_time": [5, 6, 7, 8]
    }, {
        "name": "Noodle",
        "serving_time": 3,
        "eating_time": [5, 6, 7, 8]
    }, {
        "name": "Suki",
        "serving_time": 3,
        "eating_time": [6, 7, 8, 9]
    }
]

# Value will wrap around if more or less than actual shop size
#   Empty list is uniformly weighted
food_preferences = []

tables = [
    {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }, {
        "capacity": 4
    }
]

# Flow speed
#   1 unit interval possibility: 1/7
#   2 unit interval possibility: 2/7
#   3 unit interval possibility: 2/7
#   4 unit interval possibility: 1/7
#   5 unit interval possibility: 1/7
flow_speed = [1, 2, 2, 3, 3, 4, 5]

# Group sizes
#   1 person possibility: 3/7
#   2 persons possibility: 2/7
#   3 persons possibility: 1/7
#   4 persons possibility: 1/7
group_sizes = [1, 1, 1, 2, 2, 3, 4, 5, 6]

# TODO
# - wait_for_someone_in_shop = True
#   - wait_even_table_is_free = True
#   - maximum_waiting_time = -1
# - start_eating_at_the_same_time = False

################################################################################

seed = input("Enter seed number: ")
random.seed(seed if seed else None)

name_list = [
    "Somkiat", "Sompong", "Somnamna", "Somsak", "Somsri", "Somreudee",
    "Somchai", "Somporn", "Somboon", "Somchit", "Somyod", "Somjin", "Somjai",
    "Somprat", "Somseen"
]

wait_queues = []
last_group_size = 0
next_group = None
maximum = {
    "waiting_queue": 0,
    "waiting_time": 0,
    "occupied_tables": 0
}

while True:
    #################
    # Visualization #
    #################
    # Clear screen
    print("\n" * 80)

    print("Maximum waiting queue: %s" % (maximum["waiting_queue"]))
    print("Maximum waiting time: %.2fs" % (maximum["waiting_time"]))
    print("Maximum occupied tables: %s" % (maximum["occupied_tables"]))
    next_group_time_diff = next_group - time.time() if next_group else 0
    print("Next group in %.2fs (last group is %s people)" % (
        next_group_time_diff if next_group_time_diff > 0 else 0,
        last_group_size
    ))
    shop_row = ""
    for index, shop in enumerate(food_shops):
        serving_time_diff = (
            shop["serving_end_time"] - time.time()
            if "serving_end_time" in shop else 0
        )
        shop_row += "%10s [%2.2fs : %2d]%s" % (
            shop["name"],
            serving_time_diff if serving_time_diff > 0 else 0,
            len(shop["queues"]) if "queues" in shop else 0,
            " " if index != 0 else ""
        )
    print(shop_row)
    if len(wait_queues) > 0:
        print(
            "There are %s people waiting for the table" % (len(wait_queues)) +
            " (%s[%8s] be the first one in the queue for %.2fs)" % (
                wait_queues[0]["name"], wait_queues[0]["uuid"][-8:],
                time.time() - (
                    wait_queues[0]["queue_time"]
                    if "queue_time" in wait_queues[0] else time.time()
                )
            )
        )
    else:
        print("No one waiting for the table...")
    for index, table in enumerate(tables):
        print("Table %s : %s people occupied%s%s" % (
            index + 1,
            len(table["occupations"]) if "occupations" in table else 0,
            (
                " [Group: %8s]" % (table["occupations"][0]["group_id"][-8:])
            ) if "occupations" in table else "",
            " Waiting for someone in shop..."
            if "someone_in_shop" in table and table["someone_in_shop"] else ""
        ))
        remaining_seats = table["capacity"]
        if "occupations" in table:
            remaining_seats -= len(table["occupations"])
            for occupation in table["occupations"]:
                eating_end = (
                    occupation["eating_end"] - time.time()
                    if "eating_end" in occupation else 0
                )
                print("    <%10s[%8s]> : %s" % (
                    occupation["name"],
                    occupation["uuid"][-8:],
                    "%.2fs" % (eating_end) if eating_end >= 0 else
                    "waiting for others to finish..."
                ))
        if remaining_seats > 0:
            for index in range(remaining_seats):
                print("    <Seat>")

    ########
    # Flow #
    ########
    # New group is came
    if not next_group or next_group - time.time() <= 0:
        last_group_size = random.choice(group_sizes)
        group_id = str(uuid.uuid4())
        for index in range(last_group_size):
            shop = random.choice(food_shops)
            if food_preferences:
                shop = food_shops[random.choice(food_preferences)]
            if "queues" not in shop:
                shop["queues"] = []
            shop["queues"].append({
                "name": random.choice(name_list),
                "uuid": str(uuid.uuid4()),
                "group_id": group_id
            })
        next_group = time.time() + random.choice(flow_speed) * simulation_speed
    # Update shop queues
    for shop in food_shops:
        # If order is served, serve the next person
        if (
            "serving_end_time" not in shop and
            "queues" in shop and len(shop["queues"]) > 0
        ):
            shop["serving_end_time"] = time.time() + (
                shop["serving_time"] * simulation_speed
            )
        elif (
            "serving_end_time" in shop and
            shop["serving_end_time"] - time.time() <= 0
        ):
            occupation = shop["queues"].pop()
            occupation["queue_time"] = time.time()
            occupation["eating_duration"] = (
                random.choice(shop["eating_time"]) * simulation_speed
            )
            wait_queues.append(occupation)
            del shop["serving_end_time"]

    # Update waiting queues
    wait_index = 0
    while wait_index < len(wait_queues):
        wait_queue = wait_queues[wait_index]
        got_seat = False
        free_table = None
        for table in tables:
            if "occupations" in table:
                for occupation in table["occupations"]:
                    # If there is people with the same group
                    #   and table is still free
                    if (
                        occupation["group_id"] == wait_queue["group_id"] and
                        len(table["occupations"]) < table["capacity"]
                    ):
                        table["occupations"].append(wait_queue)
                        del wait_queues[wait_index]
                        got_seat = True
                        break
            elif free_table is None:
                free_table = table
            if got_seat:
                break
        if not got_seat:
            if free_table:
                free_table["occupations"] = [wait_queue]
                del wait_queues[wait_index]
            else:
                wait_index += 1

    # Update people in tables
    for table in [t for t in tables if "occupations" in t]:
        has_free_seat = table["capacity"] - len(table["occupations"]) > 0
        everyone_is_done = True
        group_id = None
        for occupation in table["occupations"]:
            group_id = occupation["group_id"]
            if (
                "eating_end" in occupation and
                occupation["eating_end"] - time.time() > 0
            ):
                everyone_is_done = False
            elif "eating_end" not in occupation:
                occupation["eating_end"] = (
                    time.time() + occupation["eating_duration"]
                )
                everyone_is_done = False
        # If someone still in the shop queues
        someone_in_shop = False
        if has_free_seat and group_id:
            for shop in [s for s in food_shops if "queues" in s]:
                for queue in shop["queues"]:
                    if queue["group_id"] == group_id:
                        someone_in_shop = True
                        break
                if someone_in_shop:
                    break
        table["someone_in_shop"] = someone_in_shop
        if everyone_is_done and not (someone_in_shop and has_free_seat):
            del table["someone_in_shop"]
            del table["occupations"]

    # Calculate maximum
    if wait_queues:
        if maximum["waiting_queue"] < len(wait_queues):
            maximum["waiting_queue"] = len(wait_queues)
        wait_time = time.time() - (
            wait_queues[0]["queue_time"]
            if "queue_time" in wait_queues[0] else time.time()
        )
        if maximum["waiting_time"] < wait_time:
            maximum["waiting_time"] = wait_time
    maximum_tables = len([
        t for t in tables if "occupations" in t and len(t["occupations"]) > 0
    ])
    if maximum["occupied_tables"] < maximum_tables:
        maximum["occupied_tables"] = maximum_tables

    #########
    # Delay #
    #########
    time.sleep(0.1)
