/* eslint-disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

/**
 * Transaction(*, id: str = None, type: str, endpoint: str = None, started_at: datetime.datetime, finished_at: datetime.datetime = None, ellapsed: float = None, messages: List[harp.core.models.messages.Message] = None)
 */
export interface Transaction {
  id?: string
  type: string
  endpoint?: string
  started_at: string
  finished_at?: string
  ellapsed?: number
  messages?: Message[]
  [k: string]: unknown
}
/**
 * Message(*, id: int = None, transaction_id: str, kind: str, summary: str, headers: str, body: str, created_at: datetime.datetime = None)
 */
export interface Message {
  id?: number
  transaction_id: string
  kind: string
  summary: string
  headers: string
  body: string
  created_at?: string
  [k: string]: unknown
}
