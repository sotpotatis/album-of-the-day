# Last.FM API Client

A partially complete Python wrapper for the Last.FM API that implements the functions that I need for my Album of the day website.

The wrapper uses `pydantic` models to parse responses which allows better type validation.

### Implemented API methods

The following [Last.FM API methods](https://www.last.fm/api/intro) are implemented:

- `album.getInfo` - get information about an album
- `artist.getInfo` - get information about an artist
- `tag.getInfo` - get information about a tag
- `user.getRecentTracks` - retrieve scrobbles

### Changelog:

- `v.0.2.5`: Minor code quality changes. The module will also work with Pydantic versions that are not `v2.x.x`.

- `v0.2.4`: Improved deserialization for multiple fields and cases where the album only has one tag.
  This change throws things around a little bit - you do not no longer have to check that items are singular
  or a list, the module will handle that for you.

  **Breaking changes**
  _ List fields will now always return a list.
  _ Multiple fields are now optional and may return `None`.

- `v0.2.3`: Fixed a bug that crashed the deserialization if an album only had one tag, which made
  Last.FM return a dictionary rather than a list containing the tag.
- `v0.2.2`: Fixed a bug related to the loading of album images.

  **Breaking changes**

  - The field `Image.size` is now optional and may return `None`.

- `v0.2.1`: Fixed empty album text being converted to None.
- `v0.2.0`: Better handling of unset/empty Last.FM values.

  **Breaking changes:**

  - The field `Album.Tracks` is now optional and may return `None`.
  - Same applies for all image fields.
  - `v0.1.0`: Initial release
