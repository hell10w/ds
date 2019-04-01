```
ds switch-local  # to switch the context to local setup 
ds config  
ds up -d 
ds logs 
```


``` 
ds switch-remote  # to switch the context to production setup 
ds config  
ds passwd-recreate  # recreate a userpass of basic auth for nginx (default is admin:admin)
ds up -d 
ds tor-hostname  # shows url of hidden service
ds logs 
```
