from email_alerts import send_risk_alert

send_risk_alert(
    vendor_name="FTX",
    risk_score=91,
    risk_level="RED",
    summary="FTX has filed for Chapter 11 bankruptcy and faces multiple fraud charges. SEC has opened investigation. Multiple regulatory violations detected.",
    key_findings=[
        "Filed for Chapter 11 bankruptcy November 2022",
        "SEC fraud investigation opened",
        "Multiple regulatory violations detected",
    ],
    recommended_actions=[
        "Immediately review all contracts with FTX",
        "Halt any pending payments or transactions",
        "Consult legal team about exposure",
    ],
    old_score=45
)