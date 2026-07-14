// Package protocol — nơi DUY NHẤT định nghĩa topic MQTT và types.
// types.gen.go sinh từ specs/schemas — không sửa tay (make gen).
package protocol

import "fmt"

const ns = "robotops/v1"

func TopicAgentStatus(tenant, agentID string) string {
	return fmt.Sprintf("%s/%s/agents/%s/status", ns, tenant, agentID)
}
func TopicDeviceTelemetry(tenant, deviceID string) string {
	return fmt.Sprintf("%s/%s/devices/%s/telemetry", ns, tenant, deviceID)
}
// TODO(M0): bổ sung đủ theo specs/asyncapi.yaml — inventory, cmd, cmd/res, ota/state, state, events, logs.
