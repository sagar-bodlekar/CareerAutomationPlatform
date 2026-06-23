import { useEffect } from "react";

const BASE_TITLE = "DumbHorse";

/**
 * Sets the document title to `{title} | DumbHorse`.
 * Updates whenever `title` changes.
 */
export function useDocumentTitle(title: string) {
  useEffect(() => {
    document.title = title ? `${title} | ${BASE_TITLE}` : BASE_TITLE;
    return () => {
      document.title = BASE_TITLE;
    };
  }, [title]);
}
