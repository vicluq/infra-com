from tabulate import tabulate


def show_reservations(reservations: dict, connections: dict) -> str:
      data = []
      headers = ['Name', 'Room', 'Datetime']

      for res in reservations.keys():
            room, day, time = res.split('-')
            key = reservations[res]
            data.append([connections[key], room, f'{day} {time}'])
      
      return tabulate(data, headers)