
### Tables : 

#### user_table : 
	uname, password
#### license_permits : 
	uname, max_licenses, in_use
#### licenses : 
	uname, public_key, private_key, in_use, container_id, last_used
	(PK : uid, public_key) index on in_use

### APIs : 
`/user/auth` - > This API will not be used and not implemented as of now.
```
{
	username : "",
	password : ""
}
```


`/license/request`
```
Request : 
{
	username : "",
	password : "",
	container_id : ""

}

Response : 
On success
{
	status : 200,
	public_key : <license_public_key_from_db>
	message : "OK"
}

On failure
{
	status : 403,
	message : "Max Limit Reached. Please revoke licence before proceeding."
}
```

`/license/giveup`
```
Request : 
{
	username : "",
	password : "",
	public_key : <license_public_key>
	container_id : ""
}

Response : 
On success
{
	status : 200,
	public_key : <license_public_key_from_db>
	message : "Revoked"
}

On failure
If container not same as public_key assigned.
{
	status : 403,
	message : "Container id did not match."
}

{
	status : 500,
	message : "Did not revoke. Try again."
}
```

`/container/ping`
```
Request:
{
	username : "",
	password : "",
	container_id : <>,
	secret : Pk (container_id + timestamp + funny_message + container_public_key π(rolling) )
}


Response: 
{
	status : 200,
	message : "ok"
	secret : π ( Pk (funny_message + timestamp))
}

Response: 
{
	status : 403
	message : "Key revoked or container doesn't exist."
} -> action, delete Pk from container and stop computation flag.
```

##### Generating unique container id using dockerid
```
import socket
docker_short_id = socket.gethostname()

```