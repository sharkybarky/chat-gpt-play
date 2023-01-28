from steamship.invocable import PackageService
from steamship import File, Block
from steamship.data import TagKind, TagValue


class PromptService(PackageService):
    # (Optional) Adjust the randomness; 0 = no variety, 1 = lots of variety
    PROMPT_TEMPERATURE = 0.8

    # (Optional) What's the longest response you want back?
    MAX_WORDS = 400

    def complete_prompt(self, prompt_text: str) -> str:
        generator = self.client.use_plugin("prompt-generation-default",
                                           config={"max_words": self.MAX_WORDS,
                                                   "temperature": self.PROMPT_TEMPERATURE})

        block_list = [Block.CreateRequest(text=prompt_text)]
        file = File.create(self.client, blocks=block_list)

        file.tag(plugin_instance=generator.handle).wait()

        return self._generated_text(file.refresh())

    def _generated_text(self, prompt_file: File) -> str:
        """Get the generated text for a prompt file."""

        # Here, we iterate through the content blocks associated with a file
        # as well as any tags on that content to find the generated text.
        #
        # The Steamship data model provides flexible content organization,
        # storage, and lookup. Read more about the data model via:
        # https://docs.steamship.com/workspaces/data_model/index.html
        for text_block in prompt_file.blocks:
            for block_tag in text_block.tags:
                if block_tag.kind == TagKind.GENERATION:
                    return self._sanitize(block_tag.value[TagValue.STRING_VALUE])

        raise RuntimeError("Completion not found.")

    def _sanitize(self, text: str):
        """Remove any leading/trailing whitespace and partial sentences.

          This assumes that your generated output will include consistent punctuation. You may
          want to alter this method to better fit the format of your generated text.
          """
        last_punc = -1
        for i, c in enumerate(reversed(text)):
            if c in ".!?\"":
                last_punc = len(text) - i
                break
        if last_punc != -1:
            result = text[:last_punc + 1]
        else:
            result = text
        return result.strip()
