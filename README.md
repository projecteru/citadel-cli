我真的不懂为什么还要写一个这种东西
=================================

Cli for Citadel.

## Install

```shell
pip install -e git+http://gitlab.ricebook.net/platform/corecli.git#egg=core-cli --src /opt/citadel/src
```

## Configuration

配置文件就是 JSON, 放在 `~/.corecli.json`, 从 sso 上可以获取 Auth token.

```shell
cat > ~/.corecli.json << EOF
{"sso_url": "http://sso.ricebook.net", "citadel_url": "http://citadel.ricebook.net", "auth_token": "[SSO_AUTH_TOKEN]", "mimiron_url": "", "username": "[SSO_USERNAME]"}
EOF
```
