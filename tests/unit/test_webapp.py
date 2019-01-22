
async def test_process_agent_request_not_found_whitout_parameters(cli):
    resp = await cli.post('/channel', data={})
    assert resp.status == 404, "must return not found if no parameters"
