from tabulate import tabulate


def show_connections(connections: dict) -> str:
      data = []
      headers = ['Name']

      for name in connections.values():
            data.append([name])
      
      return tabulate(data, headers)