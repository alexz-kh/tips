# Flow

get all uuid => spawn items via "propotype" => get temp by id

# Zabbix conf.d conf

```
UserParameter=nvidia.smi.guery[*],bash -c '/etc/zabbix/get_nvidia_gpus.py --mode query --query $2 --gpu_uuid $1 '
UserParameter=nvidia.smi.discovery,bash -c '/etc/zabbix/get_nvidia_gpus.py --mode discovery'
```

# TODO

rewrite with
[nvidia-ml-py](https://pypi.python.org/pypi/nvidia-ml-py/)

[man](https://pythonhosted.org/nvidia-ml-py/)
