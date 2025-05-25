from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from tripmind.agents.calendar.types.calendar_state_type import CalendarState
from tripmind.agents.calendar.nodes.calendar_node import calendar_node
from tripmind.agents.common.nodes.node_wrapper import node_wrapper
from tripmind.services.calendar.google_calendar_service import GoogleCalendarService
from tripmind.clients.calendar.google_calendar_client import GoogleCalendarClient
import os


def wrap_all_nodes():
    wrapped_calendar_node = node_wrapper(
        lambda state: calendar_node(
            state,
            GoogleCalendarService(
                GoogleCalendarClient(
                    os.getenv("GOOGLE_CALENDAR_ID"),
                    os.getenv("GOOGLE_CREDENTIALS_PATH"),
                )
            ),
        )
    )

    return {
        "calendar_node": wrapped_calendar_node,
    }


def create_calendar_agent_graph():
    memory = MemorySaver()

    graph = StateGraph(CalendarState)

    wrapped_nodes = wrap_all_nodes()

    graph.add_node("calendar_node", wrapped_nodes["calendar_node"])

    graph.set_entry_point("calendar_node")

    graph.add_edge("calendar_node", END)

    return graph.compile(checkpointer=memory)


calendar_agent_graph = create_calendar_agent_graph()
