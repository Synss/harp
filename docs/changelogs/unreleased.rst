Unreleased
==========

Changed
:::::::

* Proxy: inbound message is now recorded "as-is" in the message history, without any transformation. This means that
  host and user agent headers that will be sent to the remote server are not recorded anymore, to avoid confusion
  between filtered and unfiltered content.
