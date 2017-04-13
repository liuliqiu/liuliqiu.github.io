
import stackless

sleeping_tasklets = []
sleeping_ticks = 0


def sleep(seconds_to_wait):
    channel = stackless.channel()
    end_time = sleeping_ticks + seconds_to_wait
    sleeping_tasklets.append((end_time, channel))
    sleeping_tasklets.sort()
    channel.receive()

def manage_sleeping_tasklets():
    global sleeping_ticks
    while True:
        if len(sleeping_tasklets):
            end_time, channel = sleeping_tasklets.pop(0)
            while end_time <= sleeping_ticks:
                channel.send(None)
                end_time, channel = sleeping_tasklets.pop(0)
        sleeping_ticks += 1
        print "1 second passed"
        stackless.schedule()
    pass

stackless.tasklet(manage_sleeping_tasklets)()


class AbstractClass(object):
    def get(self, items):
        while items > self.items:
            stackless.schedule()
        self.items -= items
        return items

class StoreRoom(AbstractClass):
    def __init__(self, name, product, unit, count):
        self.product = product
        self.name = name
        self.unit = unit
        self.items = count

    def get(self, count):
        while count > self.items:
            print("{} doesn't have enough {} to deliver yet".format(self.name, self.product))
            stackless.schedule()
        self.items -= count
        return count

    def put(self, count):
        self.items += count

class InjectionMolder(AbstractClass):
    def __init__(self, name, part_name, plastic_source, plastic_per_part, time_to_mod):
        self.name = name
        self.part_name = part_name
        self.plastic_source = plastic_source
        self.plastic_per_part = plastic_per_part
        self.time_to_mod = time_to_mod
        self.plastic = 0
        self.items = 0

        stackless.tasklet(self.run)()

    def run(self):
        while True:
            if self.plastic < self.plastic_per_part:
                self.plastic += self.plastic_source.get(self.plastic_per_part * 10)
            self.plastic -= self.plastic_per_part
            # sleep(self.time_to_mod)
            self.items += 1
            stackless.schedule()

class Assembler(AbstractClass):
    def __init__(self, name, part_a_source, part_b_source, rivet_source, time_to_assemble):
        self.name = name
        self.part_a_source = part_a_source
        self.part_b_source = part_b_source
        self.rivet_source = rivet_source
        self.time_to_assemble = time_to_assemble
        self.item_a = 0
        self.item_b = 0
        self.items = 0
        self.rivets = 0
        stackless.tasklet(self.run)()

    def run(self):
        while True:
            print("{} starts assembling new part".format(self.name))
            self.item_a += self.part_a_source.get(1)
            self.item_b += self.part_b_source.get(1)
            # sleep(self.time_to_assemble)
            self.items += 1
            stackless.schedule()


if __name__ == "__main__":
    rivet_store_room = StoreRoom("rivet store room", "rivets", "#", 1000)
    plastic_store_room = StoreRoom("plastic store room", "plastic pellets", "lb", 100)

    arm_molder = InjectionMolder("arm molder", "arms", plastic_store_room, 0.2, 5)
    leg_molder = InjectionMolder("leg molder", "leg", plastic_store_room, 0.2, 5)
    head_molder = InjectionMolder("head molder", "head", plastic_store_room, 0.1, 5)
    torso_molder = InjectionMolder("torso molder", "torso", plastic_store_room, 0.5, 10)

    leg_assembler = Assembler("leg assembler", torso_molder, leg_molder, rivet_store_room, 2)
    arm_assembler = Assembler("arm assembler", arm_molder, leg_assembler, rivet_store_room, 2)
    torso_assembler = Assembler("torso assembler", head_molder, arm_assembler, rivet_store_room, 3)

    stackless.run()

