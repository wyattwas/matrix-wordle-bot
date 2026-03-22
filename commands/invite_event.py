from nio import MatrixRoom, InviteEvent, AsyncClient


async def invites(room: MatrixRoom, event: InviteEvent, client: AsyncClient) -> None:
    print(f"Recieved invite to room {room.display_name} ({room.room_id}) from {event.sender}")
    await client.join(room.room_id)

