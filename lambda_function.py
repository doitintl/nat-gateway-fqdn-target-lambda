import json
import boto3
import socket
import os

ec2 = boto3.resource('ec2')

route_table_id = os.environ['route_table_id']
endpoints_name_list = os.environ['endpoints_name_list']
nat_gw_id = os.environ['nat_gw_id']

''' 
This function resolved the desired targets and returns IP list, 
the results saved into "desired_routes" since it used more than one time in the code.
'''


def resolve_endpoints(endpoints):
    endpoints_list = []
    for endpoint in endpoints.split(','):
        ips = socket.gethostbyname_ex(endpoint)
        # print(ips)
        for ip in ips[2]:
            # print(ip + "/32")
            endpoints_list.append(ip + "/32")
    print(endpoints_list)
    return endpoints_list


desired_routes = resolve_endpoints(endpoints_name_list)


# resolves the current route table with all the recordes
def get_route_table_routes(rtb):
    route_table = ec2.RouteTable(rtb)
    route_list = route_table.routes_attribute
    return route_list


# filter any route that is not associated to the relevant NAT-GW
def find_associate_routes():
    match = []
    for route in get_route_table_routes(route_table_id):
        if route.get('NatGatewayId') == nat_gw_id:
            match.append(route['DestinationCidrBlock'])
    return match


# takes the current NAT-GW routes and compare it with the DNS resolving results and returns all the routes that are not in the DNS list
def find_unused_routes():
    table_routes = find_associate_routes()
    return (list(set(table_routes) - set(desired_routes)))


# clean the route table from the NAT-GW unused IP's
def remove_routes():
    routes = find_unused_routes()
    for i in routes:
        route = ec2.Route(route_table_id, i)
        response = route.delete()
        print(response)
    return


# determinates what are the routes that should be added, and add them to the route table. 
def update_routes():
    route_table = ec2.RouteTable(route_table_id)
    changes = (list(set(desired_routes) - set(find_associate_routes())))
    for i in changes:
        route = route_table.create_route(
            DestinationCidrBlock=i,
            NatGatewayId=nat_gw_id,
        )
        print(route)
    return changes


def lambda_handler(event, context):
    print("Route table before changes: " + str(get_route_table_routes(route_table_id)))
    remove_routes()
    update_routes()
    print("Route table after changes: " + str(get_route_table_routes(route_table_id)))
    return
